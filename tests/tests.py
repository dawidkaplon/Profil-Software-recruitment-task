import script
from database import db_manager, db_parser


class TestValidator:
    """Check if data is correctly validated"""
    
    def test_email_validator(self):
        assert db_manager.DataHandler.validate_email('dawidgm.pl') is True
    
    

