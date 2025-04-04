import asyncio
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.models.account import Account
from database import get_session
from infrastructure import setup_loguru


class DBInitializer:
    """Database initializer for setting up initial data."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the database initializer.
        
        Args:
            session: The database session to use for initialization
        """
        self.session = session
        self.initialized_data: dict[str, Any] = {}

    async def ensure_system_account(self) -> Account:
        """Ensure system account exists in the database.
        
        This method will either retrieve the existing system account
        or create it if it doesn't exist.
        
        Returns:
            Account: The system account instance
        """
        system_account = await Account.get_system_account(self.session)
        self.initialized_data['system_account'] = system_account
        return system_account

    async def init_default_data(self) -> None:
        """Initialize all default data in the database.
        
        This method handles the initialization of all required default data,
        including system account, default tenants, and other necessary
        initial configurations.
        
        Raises:
            Exception: If initialization fails
        """
        try:
            # Initialize system account
            await self.ensure_system_account()
            
            # Add other default data initialization here
            # For example: default tenants, workflow templates, etc.
            
            # await self.session.commit()
            print("Successfully initialized default data")
            
        except Exception as e:
            await self.session.rollback()
            print(f"Error initializing data: {e}")
            raise


async def main(args: list[str] | None = None) -> None:
    """Main initialization function.
    
    This function sets up logging and runs the database initialization
    process. It handles the session creation and cleanup, and ensures
    proper error handling during the initialization process.
    
    Raises:
        Exception: If initialization fails
    """
    setup_loguru()
    logger.info("Starting database initialization...")
    
    try:
        async with get_session() as session:
            initializer = DBInitializer(session)
            await initializer.init_default_data()
            logger.info("Database initialization completed successfully!")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())