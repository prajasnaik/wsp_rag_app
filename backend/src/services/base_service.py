class BaseService:
    """
    Base service class that provides common functionality.
    """
    def __init__(self):
        """
        Initialize the base service.
        """
        pass
        
    def healthcheck(self):
        """
        Check if the service is healthy.
        """
        return {"status": "ok"}