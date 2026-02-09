"""
API Usage Examples and Integration Guide
Demonstrates how to use the Service Desk API programmatically
"""

import requests
import json
from datetime import datetime, timedelta


class ServiceDeskAPI:
    """Python client for IT Support Service Desk API"""
    
    def __init__(self, base_url='http://localhost:5000', admin_user=None, admin_pass=None):
        """
        Initialize API client
        
        Args:
            base_url (str): Base URL of the application
            admin_user (str): Admin username for authenticated endpoints
            admin_pass (str): Admin password
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.authenticated = False
        
        if admin_user and admin_pass:
            self.authenticate(admin_user, admin_pass)
    
    def authenticate(self, username, password):
        """Authenticate with admin portal"""
        response = self.session.post(
            f'{self.base_url}/admin/login',
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            self.authenticated = True
            print("✓ Authentication successful")
            return True
        else:
            print("✗ Authentication failed")
            return False
    
    def create_ticket(self, user_name, user_email, description, 
                     department=None, phone=None):
        """
        Create a new support ticket
        
        Args:
            user_name (str): Name of the user
            user_email (str): Email of the user
            description (str): Issue description
            department (str): User's department
            phone (str): User's phone number
            
        Returns:
            dict: Response containing ticket_id and details
        """
        payload = {
            'user_name': user_name,
            'user_email': user_email,
            'description': description,
            'department': department or '',
            'phone': phone or '',
        }
        
        response = self.session.post(
            f'{self.base_url}/api/create-ticket',
            json=payload
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✓ Ticket created: {result['ticket_id']}")
            return result
        else:
            print(f"✗ Failed to create ticket: {response.text}")
            return None
    
    def get_ticket(self, ticket_id):
        """Get ticket details by ID"""
        response = self.session.get(f'{self.base_url}/api/ticket/{ticket_id}')
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"✗ Ticket not found: {ticket_id}")
            return None
    
    def get_all_tickets(self, status=None, category=None, priority=None, 
                       date_from=None, date_to=None):
        """Get all tickets with optional filters"""
        if not self.authenticated:
            print("✗ Admin authentication required")
            return []
        
        params = {}
        if status:
            params['status'] = status
        if category:
            params['category'] = category
        if priority:
            params['priority'] = priority
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        response = self.session.get(
            f'{self.base_url}/admin/api/tickets',
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print("✗ Failed to get tickets")
            return []
    
    def update_ticket(self, ticket_id, status=None, assigned_to=None, 
                     resolution_notes=None, priority=None):
        """Update ticket details"""
        if not self.authenticated:
            print("✗ Admin authentication required")
            return False
        
        payload = {}
        if status:
            payload['status'] = status
        if assigned_to:
            payload['assigned_to'] = assigned_to
        if resolution_notes:
            payload['resolution_notes'] = resolution_notes
        if priority:
            payload['priority'] = priority
        
        response = self.session.put(
            f'{self.base_url}/admin/api/ticket/{ticket_id}',
            json=payload
        )
        
        if response.status_code == 200:
            print(f"✓ Ticket {ticket_id} updated")
            return True
        else:
            print(f"✗ Failed to update ticket: {response.text}")
            return False
    
    def get_statistics(self):
        """Get dashboard statistics"""
        if not self.authenticated:
            print("✗ Admin authentication required")
            return {}
        
        response = self.session.get(f'{self.base_url}/admin/api/statistics')
        
        if response.status_code == 200:
            return response.json()
        else:
            print("✗ Failed to get statistics")
            return {}
    
    def download_report(self, report_type='all', filename=None):
        """
        Download report in Excel format
        
        Args:
            report_type (str): 'all', 'date', or 'category'
            filename (str): Output filename (optional)
        """
        if not self.authenticated:
            print("✗ Admin authentication required")
            return False
        
        response = self.session.get(
            f'{self.base_url}/admin/api/reports/download',
            params={'type': report_type}
        )
        
        if response.status_code == 200:
            if not filename:
                filename = f'report_{report_type}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"✓ Report downloaded: {filename}")
            return True
        else:
            print("✗ Failed to download report")
            return False
    
    def get_teams(self):
        """Get support teams information"""
        if not self.authenticated:
            print("✗ Admin authentication required")
            return {}
        
        response = self.session.get(f'{self.base_url}/admin/api/teams')
        
        if response.status_code == 200:
            return response.json()
        else:
            print("✗ Failed to get teams")
            return {}


# ============================================================
# USAGE EXAMPLES
# ============================================================

def example_create_ticket():
    """Example: Create a support ticket"""
    print("\n=== Example 1: Create Ticket ===")
    
    client = ServiceDeskAPI()
    
    result = client.create_ticket(
        user_name='John Smith',
        user_email='john.smith@company.com',
        description='Cannot conect to the company WiFi netwrok from my laptop',
        department='Sales',
        phone='(555) 123-4567'
    )
    
    if result:
        print(f"Ticket ID: {result['ticket_id']}")
        print(f"Status: {result['ticket_data']['status']}")
        print(f"Assigned To: {result['ticket_data']['assigned_to']}")


def example_get_ticket():
    """Example: Retrieve ticket details"""
    print("\n=== Example 2: Get Ticket Details ===")
    
    client = ServiceDeskAPI()
    
    # First, create a ticket
    result = client.create_ticket(
        user_name='Jane Doe',
        user_email='jane.doe@company.com',
        description='Email is not working'
    )
    
    if result:
        ticket_id = result['ticket_id']
        ticket = client.get_ticket(ticket_id)
        
        if ticket:
            print(f"Ticket ID: {ticket['ticket']['ticket_id']}")
            print(f"User: {ticket['ticket']['user_name']}")
            print(f"Category: {ticket['ticket']['category']}")
            print(f"Priority: {ticket['ticket']['priority']}")
            print(f"Status: {ticket['ticket']['status']}")


def example_admin_operations():
    """Example: Admin operations"""
    print("\n=== Example 3: Admin Operations ===")
    
    client = ServiceDeskAPI(
        admin_user='admin',
        admin_pass='admin123'
    )
    
    # Get all tickets
    print("\nGetting all tickets...")
    tickets = client.get_all_tickets()
    print(f"Total tickets: {len(tickets)}")
    
    # Get open tickets
    print("\nGetting open tickets...")
    open_tickets = client.get_all_tickets(status='Open')
    print(f"Open tickets: {len(open_tickets)}")
    
    # Get critical tickets
    print("\nGetting critical tickets...")
    critical = client.get_all_tickets(priority='P1 - Critical')
    print(f"Critical tickets: {len(critical)}")
    
    # Get statistics
    print("\nGetting statistics...")
    stats = client.get_statistics()
    print(f"Total: {stats.get('total_tickets', 0)}")
    print(f"Open: {stats.get('open_tickets', 0)}")
    print(f"Resolved: {stats.get('resolved_tickets', 0)}")
    print(f"Critical: {stats.get('critical_tickets', 0)}")


def example_update_ticket():
    """Example: Update ticket status"""
    print("\n=== Example 4: Update Ticket ===")
    
    client = ServiceDeskAPI(
        admin_user='admin',
        admin_pass='admin123'
    )
    
    # Create a ticket
    result = client.create_ticket(
        user_name='Bob Johnson',
        user_email='bob.johnson@company.com',
        description='Printer not working'
    )
    
    if result:
        ticket_id = result['ticket_id']
        
        # Update the ticket
        client.update_ticket(
            ticket_id=ticket_id,
            status='In Progress',
            assigned_to='Bob Hardware',
            resolution_notes='Started troubleshooting printer connection'
        )


def example_download_reports():
    """Example: Download reports"""
    print("\n=== Example 5: Download Reports ===")
    
    client = ServiceDeskAPI(
        admin_user='admin',
        admin_pass='admin123'
    )
    
    # Download all tickets
    print("Downloading all tickets report...")
    client.download_report('all', 'all_tickets.xlsx')
    
    # Download date-wise report
    print("Downloading date-wise report...")
    client.download_report('date', 'date_wise_report.xlsx')
    
    # Download category-wise report
    print("Downloading category-wise report...")
    client.download_report('category', 'category_wise_report.xlsx')


def example_batch_processing():
    """Example: Batch processing tickets"""
    print("\n=== Example 6: Batch Processing ===")
    
    client = ServiceDeskAPI(
        admin_user='admin',
        admin_pass='admin123'
    )
    
    # Get all open network issues
    network_tickets = client.get_all_tickets(
        status='Open',
        category='Network'
    )
    
    print(f"Found {len(network_tickets)} open network tickets")
    
    # Update all of them
    for ticket in network_tickets:
        client.update_ticket(
            ticket_id=ticket['ticket_id'],
            assigned_to='John Tech',
            resolution_notes='Assigned for investigation'
        )
        print(f"Updated: {ticket['ticket_id']}")


def example_integration_with_external_system():
    """Example: Integrate with external system"""
    print("\n=== Example 7: Integration Pattern ===")
    
    # This example shows how to integrate with an external system
    # like Jira, ServiceNow, or Slack
    
    client = ServiceDeskAPI(
        admin_user='admin', 
        admin_pass='admin123'
    )
    
    # Get critical tickets
    critical_tickets = client.get_all_tickets(priority='P1 - Critical')
    
    for ticket in critical_tickets:
        # Send to external system
        print(f"\nSending {ticket['ticket_id']} to external system...")
        print(f"  Issue: {ticket['corrected_description']}")
        print(f"  Team: {ticket['assigned_to']}")
        
        # Example: Send to Slack
        # slack_client.post_message(f"Critical ticket: {ticket['ticket_id']}")
        
        # Example: Create in Jira
        # jira_client.create_issue(...)
        
        # Example: Update CRM
        # crm_client.add_note(...)


if __name__ == '__main__':
    print("IT Support Service Desk - API Usage Examples")
    print("=" * 50)
    
    # Run examples
    try:
        example_create_ticket()
        example_get_ticket()
        example_admin_operations()
        example_update_ticket()
        example_batch_processing()
        example_integration_with_external_system()
        example_download_reports()
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("Make sure the application is running on http://localhost:5000")
    
    print("\n" + "=" * 50)
    print("Examples completed!")
