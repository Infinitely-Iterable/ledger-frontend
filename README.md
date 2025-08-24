# Ledger CLI Frontend

A modern, user-friendly command-line interface for the [Ledger](https://www.ledger-cli.org/) accounting tool. This Python-based frontend provides an intuitive way to view, create, edit, and delete transactions and accounts with rich terminal output and interactive prompts.

## Features

- 🔍 **View transactions** - Multiple viewing formats (list, register, transactions)
- 💰 **Account management** - List accounts and view balances
- ✏️ **Create transactions** - Interactive transaction creation with date parsing
- 📝 **Edit transactions** - Modify existing transactions
- 🗑️ **Delete transactions** - Safe deletion with confirmation prompts
- 🎨 **Rich terminal output** - Color-coded amounts and formatted tables
- 📅 **Flexible date parsing** - Natural language date input support
- 🔧 **Ledger integration** - Works seamlessly with existing ledger files

## Requirements

- Python 3.7+
- [Ledger](https://www.ledger-cli.org/) accounting tool installed on your system
- The following Python packages (installed automatically):
  - `click` - Command-line interface framework
  - `rich` - Rich text and beautiful formatting
  - `python-dateutil` - Natural language date parsing

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ledger-frontend.git
   cd ledger-frontend
   ```

2. **Set up virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Make the wrapper script executable:**
   ```bash
   chmod +x ledger-cli
   ```

## Usage

### Basic Command Structure

```bash
./ledger-cli [OPTIONS] COMMAND [ARGS]
```

**Global Options:**
- `-f, --file TEXT` - Specify ledger file (default: `~/.ledger.dat`)
- `--help` - Show help message and exit

### Available Commands

## 📊 Viewing Commands

### `accounts`
Lists all accounts found in your ledger file.

**Usage:**
```bash
./ledger-cli accounts
./ledger-cli -f myfile.dat accounts
```

**Output:**
```
         Accounts         
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Account                ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Assets:Checking        │
│ Expenses:Food          │
│ Income:Salary          │
└────────────────────────┘
```

### `balance [account]`
Shows account balances with color-coded amounts (green for positive, red for negative).

**Usage:**
```bash
./ledger-cli balance                    # All accounts
./ledger-cli balance Assets:Checking    # Specific account
```

**Output:**
```
Account Balances

$2754.33 Assets:Checking
$1245.67 Expenses
$-3000.00 Income:Salary
```

### `list`
Displays all transactions in a clean, readable format with numbered entries.

**Usage:**
```bash
./ledger-cli list
./ledger-cli -f sample.dat list
```

**Output:**
```
All Transactions

1. 2024-01-01 Opening Balance
    Assets:Checking  $1000.00
    Equity:Opening-Balance  $-1000.00

2. 2024-01-02 Grocery Store
    Expenses:Food  $45.67
    Assets:Checking  $-45.67
```

### `transactions [account] [--limit N]`
Shows the transaction register in ledger's standard format.

**Usage:**
```bash
./ledger-cli transactions                        # All transactions
./ledger-cli transactions Assets:Checking        # Specific account
./ledger-cli transactions --limit 10             # Limit to 10 entries
```

**Options:**
- `--limit, -l INTEGER` - Limit number of transactions shown (default: 20)

### `register [account]`
Displays transactions in a detailed table format with running balances.

**Usage:**
```bash
./ledger-cli register                    # All transactions
./ledger-cli register Assets:Checking    # Specific account
```

**Output:**
```
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━┓
┃ Date       ┃ Description    ┃ Account         ┃   Amount ┃   Balance ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━┩
│ 2024-01-01 │ Opening Bal... │ Assets:Checking │ $1000.00 │  $1000.00 │
│ 2024-01-02 │ Grocery Store  │ Assets:Checking │  $-45.67 │   $954.33 │
└────────────┴────────────────┴─────────────────┴──────────┴───────────┘
```

## ✏️ Transaction Management Commands

### `create`
Interactively creates a new transaction with guided prompts.

**Usage:**
```bash
./ledger-cli create
```

**Interactive Process:**
1. **Date Entry:** Enter date in YYYY-MM-DD format or natural language (e.g., "today", "yesterday", "2024-01-15")
2. **Description:** Enter transaction description
3. **Postings:** Enter account names and amounts
   - At least 2 postings required
   - Leave amount empty for automatic balancing entry
   - Use formats like `$100.00`, `-$50.00`, `€25.50`

**Example Session:**
```
Create New Transaction

Date (YYYY-MM-DD or natural language) [2024-08-24]: today
Description: Coffee Shop
Enter postings (accounts and amounts):
Leave amount empty for the balancing entry

Account 1 (or press Enter to finish): Expenses:Food
Amount for Expenses:Food (e.g., $100.00, -$50.00, or leave empty): $4.50
Account 2 (or press Enter to finish): Assets:Checking
Amount for Assets:Checking (e.g., $100.00, -$50.00, or leave empty): 

Transaction created successfully!

Transaction added:
2024-08-24 Coffee Shop
    Expenses:Food  $4.50
    Assets:Checking
```

### `edit`
Allows editing of existing transactions through an interactive interface.

**Usage:**
```bash
./ledger-cli edit
```

**Interactive Process:**
1. **Selection:** Choose transaction from numbered list
2. **Date Modification:** Edit date (current date shown as default)
3. **Description Update:** Modify description (current description as default)
4. **Posting Changes:** Re-enter all postings (current postings displayed for reference)

**Example Session:**
```
Select Transaction to Edit
┏━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ # ┃ Date       ┃ Description    ┃ Postings   ┃
┡━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 1 │ 2024-01-01 │ Opening Bal... │ 2 postings │
│ 2 │ 2024-01-02 │ Grocery Store  │ 2 postings │
└───┴────────────┴────────────────┴────────────┘

Enter transaction number to edit: 2

Editing: 2024-01-02 Grocery Store

New date [2024-01-02]: 2024-01-02
New description [Grocery Store]: Supermarket Shopping

Current postings:
  1. Expenses:Food  $45.67
  2. Assets:Checking  $-45.67

Enter new postings:
Account 1 (or press Enter to finish): Expenses:Food
Amount for Expenses:Food: $52.30
Account 2 (or press Enter to finish): Assets:Checking
Amount for Assets:Checking: 

Transaction updated successfully!
```

### `delete`
Safely deletes transactions with confirmation prompts.

**Usage:**
```bash
./ledger-cli delete
```

**Interactive Process:**
1. **Selection:** Choose transaction from numbered list showing full posting details
2. **Confirmation:** Review selected transaction and confirm deletion
3. **Execution:** Transaction is removed from ledger file

**Example Session:**
```
Select Transaction to Delete
┏━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ # ┃ Date       ┃ Description   ┃ Postings                             ┃
┡━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1 │ 2024-01-01 │ Opening Bal...│ Assets:Checking $1000.00; Equity... │
│ 2 │ 2024-01-02 │ Grocery Store │ Expenses:Food $45.67; Assets:Che... │
└───┴────────────┴───────────────┴──────────────────────────────────────┘

Enter transaction number to delete: 2

Selected transaction:
2024-01-02 Grocery Store
    Expenses:Food  $45.67
    Assets:Checking  $-45.67

Are you sure you want to delete this transaction? [y/N]: y

Transaction deleted successfully!
```

## 📁 File Management

### Default Ledger File
By default, the tool looks for `~/.ledger.dat`. If the file doesn't exist, you'll be prompted to create it:

```
Ledger file /home/user/.ledger.dat does not exist.
Would you like to create it? [y/N]: y
Created /home/user/.ledger.dat
```

### Using Custom Files
Specify a different ledger file with the `-f` option:

```bash
./ledger-cli -f accounting/2024.dat balance
./ledger-cli -f sample.dat list
```

## 💡 Advanced Usage Tips

### Natural Language Date Parsing
The `create` command supports various date formats:
- `2024-01-15` (ISO format)
- `today`
- `yesterday`
- `Jan 15, 2024`
- `15 Jan 2024`
- `15/01/2024`

### Account Naming Conventions
Follow ledger's hierarchical account structure:
- `Assets:Checking`
- `Assets:Savings:Emergency`
- `Expenses:Food:Groceries`
- `Income:Salary:Gross`
- `Liabilities:Credit:Visa`

### Amount Formats
Support for various currencies and formats:
- `$100.00` (USD)
- `€50.25` (EUR)
- `£75.50` (GBP)
- `1000.00` (no currency symbol)
- `-$25.00` (negative amounts)

### Balancing Entries
Leave the amount empty for one posting to create a balancing entry:
```
Account 1: Expenses:Food
Amount: $25.00
Account 2: Assets:Checking
Amount: [empty] ← This will automatically be -$25.00
```

## 🔧 Integration with Ledger

This frontend is designed to work alongside the standard ledger command-line tool. You can:

1. Use this tool for day-to-day transaction management
2. Use standard ledger commands for complex reporting
3. Edit the ledger file directly when needed
4. Mix usage between this tool and ledger commands

All files created and modified by this tool are fully compatible with the standard ledger format.

## 📝 Example Workflow

1. **Start with sample data:**
   ```bash
   ./ledger-cli -f sample.dat list
   ```

2. **Check your balances:**
   ```bash
   ./ledger-cli -f sample.dat balance
   ```

3. **Add a new transaction:**
   ```bash
   ./ledger-cli -f sample.dat create
   ```

4. **Review changes:**
   ```bash
   ./ledger-cli -f sample.dat transactions --limit 5
   ```

5. **Edit if needed:**
   ```bash
   ./ledger-cli -f sample.dat edit
   ```

## 🛠️ Development

### Running Directly with Python
```bash
source venv/bin/activate
python ledger_cli.py --help
```

### File Structure
```
ledger-frontend/
├── ledger_cli.py          # Main CLI application
├── ledger-cli             # Executable wrapper script
├── requirements.txt       # Python dependencies
├── sample.dat            # Sample ledger data
├── venv/                 # Virtual environment
└── README.md             # This file
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with sample data
5. Submit a pull request

## 🐛 Troubleshooting

### "Ledger command not found"
Install ledger using your system's package manager:
- **Ubuntu/Debian:** `sudo apt-get install ledger`
- **macOS:** `brew install ledger`
- **Arch Linux:** `sudo pacman -S ledger`

### "No such file or directory"
Make sure the wrapper script is executable:
```bash
chmod +x ledger-cli
```

### Virtual Environment Issues
Recreate the virtual environment:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### File Permission Errors
Check that you have write permissions to the ledger file and directory.

## 📄 License

This project is open source. Feel free to use, modify, and distribute according to your needs.

## 🤝 Acknowledgments

- Built on top of the excellent [Ledger](https://www.ledger-cli.org/) accounting tool
- Uses [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- CLI framework provided by [Click](https://click.palletsprojects.com/)