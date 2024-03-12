from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService
from app.models import UserAccount, UserLoginData, UserRole
from app.services.base import SQLAlchemyAsyncSlugRepository


class UserAccountRepo(SQLAlchemyAsyncSlugRepository[UserAccount]):
    model_type = UserAccount


class UserAccountRepoService(SQLAlchemyAsyncRepositoryService[UserAccount]):
    repository_type = UserAccountRepo


class UserLoginDataRepo(SQLAlchemyAsyncSlugRepository[UserLoginData]):
    model_type = UserLoginData


class UserLoginDataRepoService(SQLAlchemyAsyncRepositoryService[UserLoginData]):
    repository_type = UserLoginDataRepo


class UserRoleRepo(SQLAlchemyAsyncSlugRepository[UserRole]):
    model_type = UserRole


class UserRoleRepoService(SQLAlchemyAsyncRepositoryService[UserRole]):
    repository_type = UserRoleRepo
