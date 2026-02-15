"""Authentication utilities for AWS Cognito integration."""

import json
import logging
from typing import Dict, Optional
from jose import jwk, jwt
from jose.utils import base64url_decode
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class CognitoAuthManager:
    """AWS Cognito authentication manager."""
    
    def __init__(self, user_pool_id: str, app_client_id: str, region: str = "us-east-1"):
        """Initialize Cognito auth manager."""
        self.user_pool_id = user_pool_id
        self.app_client_id = app_client_id
        self.region = region
        self.cognito_client = boto3.client('cognito-idp', region_name=region)
        self.keys_url = f"https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json"
        self._public_keys = None
    
    def get_public_keys(self) -> Dict:
        """Get public keys from Cognito."""
        if not self._public_keys:
            try:
                response = self.cognito_client.get_jwks()
                self._public_keys = {
                    key["kid"]: jwk.construct(key) for key in response["keys"]
                }
            except ClientError as e:
                logger.error(f"Error fetching public keys: {e}")
                self._public_keys = {}
        return self._public_keys
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token from Cognito."""
        try:
            # Decode token header
            headers = jwt.get_unverified_header(token)
            kid = headers.get('kid')
            
            # Get public key
            keys = self.get_public_keys()
            if kid not in keys:
                logger.error(f"Key ID {kid} not found in public keys")
                return None
            
            public_key = keys[kid]
            
            # Verify token
            claims = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                issuer=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}"
            )
            
            return claims
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with Cognito."""
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.app_client_id,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        except ClientError as e:
            logger.error(f"Error authenticating user: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token."""
        try:
            response = self.cognito_client.initiate_auth(
                ClientId=self.app_client_id,
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                }
            )
            
            return {
                'access_token': response['AuthenticationResult']['AccessToken'],
                'expires_in': response['AuthenticationResult']['ExpiresIn'],
                'token_type': response['AuthenticationResult']['TokenType']
            }
        except ClientError as e:
            logger.error(f"Error refreshing token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get user information from access token."""
        try:
            response = self.cognito_client.get_user(
                AccessToken=access_token
            )
            
            # Convert to dict format
            user_info = {
                'user_id': response['Username'],
                'attributes': {}
            }
            
            for attr in response['UserAttributes']:
                user_info['attributes'][attr['Name']] = attr['Value']
            
            return user_info
        except ClientError as e:
            logger.error(f"Error getting user info: {e}")
            return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token claims."""
    try:
        claims = jwt.get_unverified_claims(token)
        return claims.get('sub')
    except Exception as e:
        logger.error(f"Error extracting user ID from token: {e}")
        return None


def create_lambda_authorizer(auth_manager: CognitoAuthManager):
    """Create Lambda authorizer function for API Gateway."""
    def lambda_authorizer(event, context):
        """Lambda authorizer handler."""
        token = event.get('authorizationToken')
        if not token:
            return generate_policy('user', 'Deny', event['methodArn'])
        
        # Remove "Bearer " prefix if present
        if token.startswith('Bearer '):
            token = token[7:]
        
        claims = auth_manager.verify_token(token)
        if not claims:
            return generate_policy('user', 'Deny', event['methodArn'])
        
        return generate_policy(
            claims.get('sub', 'user'),
            'Allow',
            event['methodArn'],
            context=claims
        )
    
    return lambda_authorizer


def generate_policy(principal_id: str, effect: str, resource: str, context: Optional[Dict] = None) -> Dict:
    """Generate IAM policy for Lambda authorizer."""
    auth_response = {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [
                {
                    'Action': 'execute-api:Invoke',
                    'Effect': effect,
                    'Resource': resource
                }
            ]
        }
    }
    
    if context:
        auth_response['context'] = context
    
    return auth_response
