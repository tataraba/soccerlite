# from typing import TYPE_CHECKING, Any

# from litestar.contrib.jwt import OAuth2PasswordBearerAuth, Token
# from sqlalchemy import select
# from sqlalchemy.orm import joinedload, noload, selectinload

# from app import db
# from app.models import Roles, UserLoginData
# from app.services import UserService
# from app.views import urls

# from .config import get_app_settings

# if TYPE_CHECKING:
#     from litestar.connection import ASGIConnection, Request

# settings = get_app_settings()


# async def provide_user(request: Request[UserLoginData, Token, Any]) -> UserLoginData:
#     """Get the user from the connection."""
#     return request.user


# async def current_user_from_token(
#     token: Token, connection: ASGIConnection[Any, Any, Any, Any]
# ) -> UserLoginData | None:
#     """Lookup current user from local JWT token.

#     Fetches the user information from the database

#     Args:
#         token (str): JWT Token Object
#         connection (ASGIConnection[Any, Any, Any, Any]): ASGI connection.


#     Returns:
#         User: User record mapped to the JWT identifier
#     """

#     async with UserService.new(
#         session=db.config.provide_session(connection.app.state, connection.scope),
#         statement=select(UserLoginData).options(
#             noload("*"),
#             selectinload(UserLoginData.roles).options(
#                 joinedload(TeamMember.team, innerjoin=True).options(
#                     noload("*"),
#                 ),
#             ),
#         ),
#     ) as service:
#         user = await service.get_user_by(email=token.sub)
#         if user and user.is_active:
#             return user
#     return None
