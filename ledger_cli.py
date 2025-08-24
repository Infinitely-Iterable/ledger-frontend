#!/usr/bin/env python3
"""
Ledger CLI Frontend - A simple CLI interface for the Ledger accounting tool
"""

import os
import sys
import subprocess
import re
from datetime import datetime
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.text import Text
from dateutil.parser import parse as parse_date

console = Console()

class LedgerManager:
    def __init__(self, ledger_file=None):
        self.ledger_file = ledger_file or os.path.expanduser("~/.ledger.dat")
        
    def run_ledger_command(self, command, args=None):
        """Run a ledger command and return the output"""
        cmd = ["ledger", "-f", self.ledger_file]
        if args:
            cmd.extend(args)
        cmd.append(command)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Error running ledger command: {e.stderr}[/red]")
            return None
        except FileNotFoundError:
            console.print("[red]Ledger command not found. Please install ledger.[/red]")
            return None

    def get_accounts(self):
        """Get list of all accounts"""
        output = self.run_ledger_command("accounts")
        return output.split('\n') if output else []

    def get_transactions(self, account=None):
        """Get transaction register"""
        args = [account] if account else []
        return self.run_ledger_command("register", args)

    def get_balance(self, account=None):
        """Get account balances"""
        args = [account] if account else []
        return self.run_ledger_command("balance", args)
    
    def add_transaction(self, date, description, postings):
        """Add a new transaction to the ledger file"""
        if not os.path.exists(self.ledger_file):
            Path(self.ledger_file).touch()
        
        transaction = f"{date} {description}\n"
        for account, amount in postings:
            if amount:
                transaction += f"    {account}  {amount}\n"
            else:
                transaction += f"    {account}\n"
        transaction += "\n"
        
        with open(self.ledger_file, 'a', encoding='utf-8') as f:
            f.write(transaction)
    
    def read_transactions(self):
        """Read all transactions from the ledger file"""
        if not os.path.exists(self.ledger_file):
            return []
        
        with open(self.ledger_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
    
    def write_transactions(self, content):
        """Write transactions back to the ledger file"""
        with open(self.ledger_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def parse_transactions(self, content):
        """Parse transactions from ledger file content"""
        transactions = []
        current_transaction = None
        
        for line_num, line in enumerate(content.split('\n'), 1):
            line = line.rstrip()
            
            if not line or line.startswith(';'):
                continue
            
            if not line.startswith('    ') and not line.startswith('\t'):
                if current_transaction:
                    transactions.append(current_transaction)
                
                parts = line.split(' ', 1)
                if len(parts) >= 2:
                    current_transaction = {
                        'line_start': line_num,
                        'date': parts[0],
                        'description': parts[1],
                        'postings': []
                    }
            elif current_transaction and (line.startswith('    ') or line.startswith('\t')):
                posting_line = line.strip()
                if posting_line:
                    account_match = re.match(r'^([^$\d-]+)\s*(.*)$', posting_line)
                    if account_match:
                        account = account_match.group(1).strip()
                        amount = account_match.group(2).strip() if account_match.group(2) else ""
                        current_transaction['postings'].append((account, amount))
        
        if current_transaction:
            transactions.append(current_transaction)
        
        return transactions

ledger = LedgerManager()

@click.group()
@click.option('--file', '-f', 'ledger_file', 
              help='Ledger file to use (default: ~/.ledger.dat)')
def cli(ledger_file):
    """Ledger CLI Frontend - Manage your accounting data"""
    if ledger_file:
        ledger.ledger_file = ledger_file
    
    if not os.path.exists(ledger.ledger_file):
        console.print(f"[yellow]Ledger file {ledger.ledger_file} does not exist.[/yellow]")
        if Confirm.ask("Would you like to create it?"):
            Path(ledger.ledger_file).touch()
            console.print(f"[green]Created {ledger.ledger_file}[/green]")
        else:
            console.print("[red]Cannot proceed without a ledger file.[/red]")
            sys.exit(1)

@cli.command()
def accounts():
    """List all accounts"""
    accounts_list = ledger.get_accounts()
    if not accounts_list:
        console.print("[yellow]No accounts found.[/yellow]")
        return
    
    table = Table(title="Accounts")
    table.add_column("Account", style="cyan")
    
    for account in accounts_list:
        if account.strip():
            table.add_row(account)
    
    console.print(table)

@cli.command()
@click.argument('account', required=False)
def balance(account):
    """Show account balances (optionally for a specific account)"""
    balance_output = ledger.get_balance(account)
    if not balance_output:
        console.print("[yellow]No balance information found.[/yellow]")
        return
    
    console.print("[bold]Account Balances[/bold]")
    console.print()
    
    lines = balance_output.split('\n')
    for line in lines:
        if line.strip():
            parts = line.strip().split()
            if len(parts) >= 2:
                amount = parts[0]
                account_name = ' '.join(parts[1:])
                
                if amount.startswith('-'):
                    amount_text = Text(amount, style="red")
                else:
                    amount_text = Text(amount, style="green")
                
                console.print(f"{amount_text} {account_name}")

@cli.command()
@click.argument('account', required=False)
@click.option('--limit', '-l', default=20, help='Limit number of transactions shown')
def transactions(account, limit):
    """Show transaction register (optionally for a specific account)"""
    register_output = ledger.get_transactions(account)
    if not register_output:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    console.print(f"[bold]Transaction Register{' for ' + account if account else ''}[/bold]")
    console.print()
    
    lines = register_output.split('\n')
    count = 0
    
    for line in lines:
        if line.strip() and count < limit:
            console.print(line)
            count += 1
    
    if len(lines) > limit:
        console.print(f"[dim]... and {len(lines) - limit} more transactions (use --limit to see more)[/dim]")

@cli.command()
@click.argument('account', required=False)
def register(account):
    """Show detailed transaction register"""
    register_output = ledger.get_transactions(account)
    if not register_output:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    table = Table(title=f"Transaction Register{' for ' + account if account else ''}")
    table.add_column("Date", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Account", style="yellow")
    table.add_column("Amount", justify="right")
    table.add_column("Balance", justify="right", style="bold")
    
    lines = register_output.split('\n')
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) >= 5:
                date = parts[0]
                desc_end = -3
                for i, part in enumerate(parts[1:], 1):
                    if part.startswith('$') or part.startswith('-$'):
                        desc_end = i
                        break
                
                description = ' '.join(parts[1:desc_end])
                account_name = ' '.join(parts[desc_end:-2])
                amount = parts[-2]
                balance = parts[-1]
                
                amount_style = "red" if amount.startswith('-') else "green"
                balance_style = "red" if balance.startswith('-') else "green"
                
                table.add_row(
                    date,
                    description,
                    account_name,
                    Text(amount, style=amount_style),
                    Text(balance, style=balance_style)
                )
    
    console.print(table)

@cli.command()
def create():
    """Create a new transaction interactively"""
    console.print("[bold cyan]Create New Transaction[/bold cyan]")
    console.print()
    
    date_str = Prompt.ask("Date (YYYY-MM-DD or natural language)", default=datetime.now().strftime("%Y-%m-%d"))
    
    try:
        parsed_date = parse_date(date_str)
        date_formatted = parsed_date.strftime("%Y-%m-%d")
    except:
        console.print("[red]Invalid date format. Using today's date.[/red]")
        date_formatted = datetime.now().strftime("%Y-%m-%d")
    
    description = Prompt.ask("Description")
    
    postings = []
    console.print("\n[bold]Enter postings (accounts and amounts):[/bold]")
    console.print("[dim]Leave amount empty for the balancing entry[/dim]")
    
    while True:
        account = Prompt.ask(f"Account {len(postings) + 1} (or press Enter to finish)", default="")
        if not account:
            break
            
        amount = Prompt.ask(f"Amount for {account} (e.g., $100.00, -$50.00, or leave empty)", default="")
        postings.append((account, amount))
        
        if len(postings) >= 2 and not amount:
            break
    
    if len(postings) < 2:
        console.print("[red]A transaction must have at least 2 postings.[/red]")
        return
    
    try:
        ledger.add_transaction(date_formatted, description, postings)
        console.print(f"[green]Transaction created successfully![/green]")
        
        console.print("\n[bold]Transaction added:[/bold]")
        console.print(f"{date_formatted} {description}")
        for account, amount in postings:
            if amount:
                console.print(f"    {account}  {amount}")
            else:
                console.print(f"    {account}")
        
    except Exception as e:
        console.print(f"[red]Error creating transaction: {e}[/red]")

@cli.command()
def edit():
    """Edit an existing transaction"""
    content = ledger.read_transactions()
    if not content:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    transactions = ledger.parse_transactions(content)
    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    console.print("[bold cyan]Select Transaction to Edit[/bold cyan]")
    table = Table()
    table.add_column("#", style="cyan")
    table.add_column("Date", style="white")
    table.add_column("Description", style="yellow")
    table.add_column("Postings", style="dim")
    
    for i, trans in enumerate(transactions):
        posting_summary = f"{len(trans['postings'])} postings"
        table.add_row(str(i + 1), trans['date'], trans['description'], posting_summary)
    
    console.print(table)
    
    try:
        choice = int(Prompt.ask("Enter transaction number to edit")) - 1
        if choice < 0 or choice >= len(transactions):
            console.print("[red]Invalid selection.[/red]")
            return
    except ValueError:
        console.print("[red]Invalid input.[/red]")
        return
    
    selected = transactions[choice]
    console.print(f"\n[bold]Editing: {selected['date']} {selected['description']}[/bold]")
    
    new_date = Prompt.ask("New date", default=selected['date'])
    new_description = Prompt.ask("New description", default=selected['description'])
    
    console.print("\n[bold]Current postings:[/bold]")
    for i, (account, amount) in enumerate(selected['postings']):
        console.print(f"  {i + 1}. {account}  {amount}")
    
    new_postings = []
    console.print("\n[bold]Enter new postings:[/bold]")
    
    while True:
        account = Prompt.ask(f"Account {len(new_postings) + 1} (or press Enter to finish)", default="")
        if not account:
            break
            
        amount = Prompt.ask(f"Amount for {account}", default="")
        new_postings.append((account, amount))
    
    if len(new_postings) < 2:
        console.print("[red]A transaction must have at least 2 postings.[/red]")
        return
    
    try:
        lines = content.split('\n')
        new_lines = []
        skip_lines = 0
        
        for i, line in enumerate(lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
                
            if not line.strip() or line.startswith(';'):
                new_lines.append(line)
                continue
            
            if not line.startswith('    ') and not line.startswith('\t'):
                parts = line.split(' ', 1)
                if len(parts) >= 2 and parts[0] == selected['date'] and parts[1] == selected['description']:
                    new_transaction = f"{new_date} {new_description}"
                    new_lines.append(new_transaction)
                    
                    for account, amount in new_postings:
                        if amount:
                            new_lines.append(f"    {account}  {amount}")
                        else:
                            new_lines.append(f"    {account}")
                    
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('    ') or lines[j].startswith('\t') or not lines[j].strip()):
                        skip_lines += 1
                        j += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        ledger.write_transactions('\n'.join(new_lines))
        console.print("[green]Transaction updated successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error updating transaction: {e}[/red]")

@cli.command()
def delete():
    """Delete an existing transaction"""
    content = ledger.read_transactions()
    if not content:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    transactions = ledger.parse_transactions(content)
    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    console.print("[bold red]Select Transaction to Delete[/bold red]")
    table = Table()
    table.add_column("#", style="cyan")
    table.add_column("Date", style="white")
    table.add_column("Description", style="yellow")
    table.add_column("Postings", style="dim")
    
    for i, trans in enumerate(transactions):
        posting_details = []
        for account, amount in trans['postings']:
            posting_details.append(f"{account} {amount}".strip())
        posting_summary = "; ".join(posting_details)
        table.add_row(str(i + 1), trans['date'], trans['description'], posting_summary)
    
    console.print(table)
    
    try:
        choice = int(Prompt.ask("Enter transaction number to delete")) - 1
        if choice < 0 or choice >= len(transactions):
            console.print("[red]Invalid selection.[/red]")
            return
    except ValueError:
        console.print("[red]Invalid input.[/red]")
        return
    
    selected = transactions[choice]
    console.print(f"\n[bold]Selected transaction:[/bold]")
    console.print(f"{selected['date']} {selected['description']}")
    for account, amount in selected['postings']:
        console.print(f"    {account}  {amount}")
    
    if not Confirm.ask("\n[red]Are you sure you want to delete this transaction?[/red]"):
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return
    
    try:
        lines = content.split('\n')
        new_lines = []
        skip_lines = 0
        
        for i, line in enumerate(lines):
            if skip_lines > 0:
                skip_lines -= 1
                continue
                
            if not line.strip() or line.startswith(';'):
                new_lines.append(line)
                continue
            
            if not line.startswith('    ') and not line.startswith('\t'):
                parts = line.split(' ', 1)
                if len(parts) >= 2 and parts[0] == selected['date'] and parts[1] == selected['description']:
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('    ') or lines[j].startswith('\t') or not lines[j].strip()):
                        skip_lines += 1
                        j += 1
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        
        ledger.write_transactions('\n'.join(new_lines))
        console.print("[green]Transaction deleted successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error deleting transaction: {e}[/red]")

@cli.command()
def list():
    """List all transactions in a readable format"""
    content = ledger.read_transactions()
    if not content:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    transactions = ledger.parse_transactions(content)
    if not transactions:
        console.print("[yellow]No transactions found.[/yellow]")
        return
    
    console.print("[bold cyan]All Transactions[/bold cyan]\n")
    
    for i, trans in enumerate(transactions):
        console.print(f"[bold]{i + 1}. {trans['date']} {trans['description']}[/bold]")
        for account, amount in trans['postings']:
            if amount:
                amount_text = Text(amount, style="green" if not amount.startswith('-') else "red")
                console.print(f"    {account}  {amount_text}")
            else:
                console.print(f"    {account}")
        console.print()

if __name__ == "__main__":
    cli()