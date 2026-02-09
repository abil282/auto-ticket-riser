"""
Ticket Assignment and Routing Module
Rule-based logic for automatic ticket assignment to support teams
"""

import json


class TicketRouter:
    """Route tickets to appropriate support teams based on rules"""
    
    # Default support teams and their expertise
    SUPPORT_TEAMS = {
        'Network Support': {
            'email': 'network-support@company.com',
            'members': ['John Tech', 'Sarah Net'],
            'expertise': ['network', 'connection', 'wifi', 'internet', 'lan', 'vpn'],
            'max_capacity': 20
        },
        'Email & Collaboration': {
            'email': 'email-support@company.com',
            'members': ['Mike Mail', 'Emma Send'],
            'expertise': ['email', 'outlook', 'exchange', 'teams', 'sharepoint'],
            'max_capacity': 15
        },
        'Access & Security': {
            'email': 'access-support@company.com',
            'members': ['Alex Auth', 'Diana Access'],
            'expertise': ['login', 'authentication', 'credentials', 'password', 'access', 'active directory', 'ad'],
            'max_capacity': 20
        },
        'Hardware Support': {
            'email': 'hardware-support@company.com',
            'members': ['Bob Hardware', 'Carol PC'],
            'expertise': ['monitor', 'keyboard', 'mouse', 'printer', 'hardware', 'device', 'laptop'],
            'max_capacity': 15
        },
        'Software Support': {
            'email': 'software-support@company.com',
            'members': ['Tom App', 'Lisa Update'],
            'expertise': ['software', 'application', 'installation', 'update', 'patch', 'license'],
            'max_capacity': 20
        },
        'Database Support': {
            'email': 'database-support@company.com',
            'members': ['Dave DB', 'Nina Data'],
            'expertise': ['database', 'sql', 'backend', 'data', 'query'],
            'max_capacity': 10
        },
        'Security Team': {
            'email': 'security-support@company.com',
            'members': ['Steve Security', 'Victoria Guard'],
            'expertise': ['security', 'antivirus', 'firewall', 'vpn', 'encryption', 'malware'],
            'max_capacity': 12
        },
        'Performance Team': {
            'email': 'performance-support@company.com',
            'members': ['Pete Speed', 'Rose Fast'],
            'expertise': ['slow', 'crash', 'freeze', 'hang', 'performance', 'speed', 'lag'],
            'max_capacity': 18
        },
        'General Support': {
            'email': 'general-support@company.com',
            'members': ['Susan Help', 'Paul Support'],
            'expertise': [],
            'max_capacity': 30
        }
    }
    
    # Priority-based SLA
    SLA_TARGETS = {
        'P1 - Critical': {
            'response_hours': 1,
            'resolution_hours': 4,
            'escalate_to': ['General Support']
        },
        'P2 - High': {
            'response_hours': 2,
            'resolution_hours': 8,
            'escalate_to': ['General Support']
        },
        'P3 - Medium': {
            'response_hours': 4,
            'resolution_hours': 24,
            'escalate_to': ['General Support']
        },
        'P4 - Low': {
            'response_hours': 24,
            'resolution_hours': 72,
            'escalate_to': []
        }
    }
    
    def __init__(self):
        """Initialize router"""
        self.routing_rules = self._load_routing_rules()
        self.team_workload = {team: 0 for team in self.SUPPORT_TEAMS.keys()}
    
    def _load_routing_rules(self):
        """Load routing rules from configuration"""
        return {
            'network': 'Network Support',
            'connection': 'Network Support',
            'wifi': 'Network Support',
            'internet': 'Network Support',
            'connectivity': 'Network Support',
            'lan': 'Network Support',
            'vpn': 'Network Support',
            
            'email': 'Email & Collaboration',
            'outlook': 'Email & Collaboration',
            'exchange': 'Email & Collaboration',
            'teams': 'Email & Collaboration',
            'sharepoint': 'Email & Collaboration',
            
            'login': 'Access & Security',
            'authentication': 'Access & Security',
            'credentials': 'Access & Security',
            'password': 'Access & Security',
            'ad': 'Access & Security',
            'active directory': 'Access & Security',
            
            'monitor': 'Hardware Support',
            'keyboard': 'Hardware Support',
            'mouse': 'Hardware Support',
            'printer': 'Hardware Support',
            'device': 'Hardware Support',
            'laptop': 'Hardware Support',
            'desktop': 'Hardware Support',
            
            'software': 'Software Support',
            'application': 'Software Support',
            'installation': 'Software Support',
            'update': 'Software Support',
            'patch': 'Software Support',
            'license': 'Software Support',
            
            'database': 'Database Support',
            'sql': 'Database Support',
            'backend': 'Database Support',
            
            'security': 'Security Team',
            'antivirus': 'Security Team',
            'firewall': 'Security Team',
            'encryption': 'Security Team',
            'malware': 'Security Team',
            
            'slow': 'Performance Team',
            'crash': 'Performance Team',
            'freeze': 'Performance Team',
            'hang': 'Performance Team',
            'performance': 'Performance Team',
            'speed': 'Performance Team',
            'lag': 'Performance Team',
        }
    
    def route_ticket(self, ticket_data):
        """
        Route ticket to appropriate team based on category and priority
        
        Args:
            ticket_data (dict): Processed ticket data
            
        Returns:
            dict: Routing decision with team assignment
        """
        category = ticket_data.get('category', 'General').lower()
        priority = ticket_data.get('priority', 'P3 - Medium')
        description = ticket_data.get('corrected_description', '').lower()
        
        # Find best matching team
        assigned_team = self._determine_team(category, description)
        
        # Get specific team member based on workload
        team_member = self._assign_team_member(assigned_team)
        
        # Get SLA information
        sla = self.SLA_TARGETS.get(priority, self.SLA_TARGETS['P3 - Medium'])
        
        return {
            'assigned_team': assigned_team,
            'assigned_to': team_member,
            'team_email': self.SUPPORT_TEAMS[assigned_team]['email'],
            'priority': priority,
            'sla_response_hours': sla['response_hours'],
            'sla_resolution_hours': sla['resolution_hours'],
            'routing_reason': f"Matched team based on category: {category}"
        }
    
    def _determine_team(self, category, description):
        """Determine the best team for the ticket"""
        # First try category match
        for keyword, team in self.routing_rules.items():
            if keyword in category.lower():
                return team
        
        # Then try keywords in description
        words = description.split()
        for word in words:
            if word in self.routing_rules:
                return self.routing_rules[word]
        
        # Default to General Support
        return 'General Support'
    
    def _assign_team_member(self, team_name):
        """
        Assign specific team member with load balancing
        
        Args:
            team_name (str): Name of the team
            
        Returns:
            str: Assigned team member name
        """
        team = self.SUPPORT_TEAMS.get(team_name)
        if not team or not team['members']:
            return 'Unassigned'
        
        # For now, return first available member
        # In production, use load balancing from actual workload
        return team['members'][0]
    
    def get_team_info(self, team_name):
        """Get detailed team information"""
        return self.SUPPORT_TEAMS.get(team_name, {})
    
    def get_all_teams(self):
        """Get list of all support teams"""
        return list(self.SUPPORT_TEAMS.keys())
    
    def get_sla_targets(self, priority):
        """Get SLA targets for a priority level"""
        return self.SLA_TARGETS.get(priority, self.SLA_TARGETS['P3 - Medium'])


class TicketAssignment:
    """High-level ticket assignment coordinator"""
    
    def __init__(self):
        """Initialize assignment coordinator"""
        self.router = TicketRouter()
    
    def assign_ticket(self, ticket_data):
        """
        Assign a ticket with full business logic
        
        Args:
            ticket_data (dict): Ticket information including processed data
            
        Returns:
            dict: Complete assignment details
        """
        routing = self.router.route_ticket(ticket_data)
        
        assignment = {
            'ticket_id': ticket_data.get('ticket_id'),
            'assigned_team': routing['assigned_team'],
            'assigned_to': routing['assigned_to'],
            'team_email': routing['team_email'],
            'priority': routing['priority'],
            'sla_response_hours': routing['sla_response_hours'],
            'sla_resolution_hours': routing['sla_resolution_hours'],
            'status': 'Assigned',
            'assignment_timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        return assignment
