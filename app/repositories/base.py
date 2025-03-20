class BaseRepository:
    """Base repository class with common transaction handling methods."""

    def __init__(self, session):
        self.session = session

    async def commit(self):
        """Commit the current transaction."""
        try:
            await self.session.commit()
        except Exception as e:
            await self.session.rollback()
            raise e

    async def rollback(self):
        """Rollback the current transaction."""
        await self.session.rollback()
