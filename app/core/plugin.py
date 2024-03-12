from litestar.contrib.jwt import JWTCookieAuth
from litestar_users import LitestarUsersConfig, LitestarUsersPlugin  # type: ignore
from litestar_users.config import (  # type: ignore
    AuthHandlerConfig,
    CurrentUserHandlerConfig,
    PasswordResetHandlerConfig,
    RegisterHandlerConfig,
    RoleManagementHandlerConfig,
    UserManagementHandlerConfig,
    VerificationHandlerConfig,
)

from app import db, models
from app.dto.user import (
    RoleCreateDTO,
    RoleReadDTO,
    RoleUpdateDTO,
    UserReadDTO,
    UserRegistrationDTO,
    UserUpdateDTO,
)
from app.services.account.user import UserAccountRepoService

from . import get_app_settings

settings = get_app_settings()

__all__ = [
    "LitestarUsersPlugin",
    "LitestarUsersConfig",
    "users_plugin",
    "db_plugin",
]


users_plugin = LitestarUsersPlugin(
    config=LitestarUsersConfig(
        auth_backend_class=JWTCookieAuth,
        secret=settings.ENCODING_SECRET,
        user_model=models.UserLoginData,
        user_read_dto=UserReadDTO,
        user_registration_dto=UserRegistrationDTO,
        user_update_dto=UserUpdateDTO,
        role_model=models.Roles,
        role_read_dto=RoleReadDTO,
        role_create_dto=RoleCreateDTO,
        role_update_dto=RoleUpdateDTO,
        user_service_class=UserAccountRepoService,  # type: ignore
        auth_exclude_paths=["/", "/schema", "/login", "/register", "/secret_admin"],
        auth_handler_config=AuthHandlerConfig(),
        current_user_handler_config=CurrentUserHandlerConfig(),
        password_reset_handler_config=PasswordResetHandlerConfig(),
        register_handler_config=RegisterHandlerConfig(),
        role_management_handler_config=RoleManagementHandlerConfig(),
        user_management_handler_config=UserManagementHandlerConfig(),
        verification_handler_config=VerificationHandlerConfig(),
    )
)

db_plugin = db.plugin
