"""
Service Desk Automation System Modules
"""

from .spelling_corrector import SpellingCorrector, spelling_corrector
from .database import TicketDatabase, ExcelReportGenerator
from .ticket_router import TicketRouter, TicketAssignment
from .email_integration import Office365Integration, EmailTicketParser

__all__ = [
    'SpellingCorrector',
    'spelling_corrector',
    'TicketDatabase',
    'ExcelReportGenerator',
    'TicketRouter',
    'TicketAssignment',
    'Office365Integration',
    'EmailTicketParser'
]
