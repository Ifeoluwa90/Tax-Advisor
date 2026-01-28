"""
Tax Contribution Advisor v2
Loads tax data from JSON files for easy updates.

Run tax_data_updater.py first to generate the data files.
"""

import json
import os

# ====================
# DATA LOADING
# ====================

DATA_DIR = "tax_data"
COMBINED_DATA_FILE = os.path.join(DATA_DIR, "tax_data.json")

def load_tax_data():
    """Load tax data from JSON file."""
    if not os.path.exists(COMBINED_DATA_FILE):
        print(f"Warning: {COMBINED_DATA_FILE} not found.")
        print("Run tax_data_updater.py first to generate data files.")
        print("Using fallback built-in data.\n")
        return None
    
    with open(COMBINED_DATA_FILE, 'r') as f:
        return json.load(f)


# Load data at module level
TAX_DATA = load_tax_data()


# ====================
# FALLBACK DATA (if JSON not available)
# ====================

FALLBACK_FEDERAL_SINGLE = [
    (11925, 0.10),
    (48475, 0.12),
    (103350, 0.22),
    (197300, 0.24),
    (250525, 0.32),
    (626350, 0.35),
    (float('inf'), 0.37)
]

FALLBACK_STANDARD_DEDUCTION = {
    "single": 15000,
    "married": 30000,
    "head_of_household": 22500
}

FALLBACK_STATE_RATES = {
    "WA": 0.00, "OR": 0.099, "CA": 0.133, "TX": 0.00, "FL": 0.00,
    "NY": 0.109, "IL": 0.0495, "PA": 0.0307, "OH": 0.035, "GA": 0.0539
}

# Contribution limits (2025)
CONTRIBUTION_LIMITS = {
    "401k": 23500,
    "401k_catch_up": 7500,
    "ira": 7000,
    "ira_catch_up": 1000
}


# ====================
# TAX CALCULATIONS
# ====================

def get_federal_brackets(filing_status):
    """Get federal tax brackets for filing status."""
    if TAX_DATA:
        fed_data = TAX_DATA.get("federal", {})
        brackets_list = fed_data.get(filing_status, fed_data.get("single", []))
        # Convert from JSON format to tuple format
        return [(b.get("max") or float('inf'), b["rate"]) for b in brackets_list]
    return FALLBACK_FEDERAL_SINGLE


def get_standard_deduction(filing_status):
    """Get standard deduction for filing status."""
    if TAX_DATA:
        fed_data = TAX_DATA.get("federal", {})
        deductions = fed_data.get("standard_deduction", {})
        return deductions.get(filing_status, 15000)
    return FALLBACK_STANDARD_DEDUCTION.get(filing_status, 15000)


def get_state_rate(state):
    """Get state tax rate."""
    state = state.upper()
    if TAX_DATA:
        states = TAX_DATA.get("states", {})
        state_info = states.get(state, {})
        return state_info.get("top_rate", 0)
    return FALLBACK_STATE_RATES.get(state, 0)


def get_state_info(state):
    """Get full state info including name and type."""
    state = state.upper()
    if TAX_DATA:
        states = TAX_DATA.get("states", {})
        return states.get(state, {"name": state, "top_rate": 0, "type": "unknown"})
    return {"name": state, "top_rate": FALLBACK_STATE_RATES.get(state, 0), "type": "unknown"}


def get_all_states():
    """Get list of all state codes."""
    if TAX_DATA:
        return list(TAX_DATA.get("states", {}).keys())
    return list(FALLBACK_STATE_RATES.keys())


def calculate_federal_tax(taxable_income, filing_status="single"):
    """Calculate federal income tax using progressive brackets."""
    brackets = get_federal_brackets(filing_status)
    tax = 0
    prev_limit = 0
    
    for limit, rate in brackets:
        if taxable_income <= prev_limit:
            break
        taxable_in_bracket = min(taxable_income, limit) - prev_limit
        tax += taxable_in_bracket * rate
        prev_limit = limit
    
    return tax


def get_marginal_federal_rate(taxable_income, filing_status="single"):
    """Get the marginal federal tax rate for a given income."""
    brackets = get_federal_brackets(filing_status)
    
    for limit, rate in brackets:
        if taxable_income <= limit:
            return rate
    
    return brackets[-1][1]


def calculate_state_tax(income, state):
    """Calculate state tax (simplified using top rate)."""
    return income * get_state_rate(state)


# ====================
# ROTH VS TRADITIONAL ANALYSIS
# ====================

def analyze_contribution(
    gross_income,
    state,
    filing_status="single",
    age=30,
    contribution_amount=None,
    expected_retirement_rate=None
):
    """
    Analyze whether Roth or Traditional contribution is better.
    """
    # Get standard deduction
    std_deduction = get_standard_deduction(filing_status)
    
    # Calculate taxable income
    taxable_income = max(0, gross_income - std_deduction)
    
    # Get current tax rates
    federal_marginal_rate = get_marginal_federal_rate(taxable_income, filing_status)
    state_rate = get_state_rate(state)
    combined_rate = federal_marginal_rate + state_rate
    
    # Calculate current taxes
    federal_tax = calculate_federal_tax(taxable_income, filing_status)
    state_tax = calculate_state_tax(taxable_income, state)
    total_tax = federal_tax + state_tax
    
    # Contribution limits
    limit_401k = CONTRIBUTION_LIMITS["401k"]
    limit_ira = CONTRIBUTION_LIMITS["ira"]
    if age >= 50:
        limit_401k += CONTRIBUTION_LIMITS["401k_catch_up"]
        limit_ira += CONTRIBUTION_LIMITS["ira_catch_up"]
    
    # Default contribution for analysis
    if contribution_amount is None:
        contribution_amount = min(6000, limit_401k)
    
    # Tax savings if Traditional
    traditional_tax_savings = contribution_amount * combined_rate
    
    # Build recommendation
    state_info = get_state_info(state)
    recommendation = build_recommendation(
        federal_marginal_rate,
        state_rate,
        combined_rate,
        expected_retirement_rate,
        state,
        state_info
    )
    
    return {
        "gross_income": gross_income,
        "standard_deduction": std_deduction,
        "taxable_income": taxable_income,
        "federal_marginal_rate": federal_marginal_rate,
        "state_rate": state_rate,
        "combined_marginal_rate": combined_rate,
        "federal_tax": federal_tax,
        "state_tax": state_tax,
        "total_tax": total_tax,
        "contribution_limits": {
            "401k": limit_401k,
            "ira": limit_ira
        },
        "traditional_tax_savings": traditional_tax_savings,
        "recommendation": recommendation,
        "data_year": TAX_DATA.get("data_year", 2025) if TAX_DATA else 2025,
        "last_updated": TAX_DATA.get("last_updated", "unknown") if TAX_DATA else "unknown"
    }


def build_recommendation(fed_rate, state_rate, combined_rate, expected_retirement_rate, state, state_info):
    """Build a recommendation based on tax rates."""
    
    reasons = []
    recommendation = ""
    
    # Low federal bracket (10% or 12%)
    if fed_rate <= 0.12:
        reasons.append(f"You're in the {fed_rate*100:.0f}% federal bracket — historically low")
        recommendation = "ROTH"
    elif fed_rate == 0.22:
        reasons.append(f"You're in the 22% federal bracket — moderate rate")
        recommendation = "CONSIDER BOTH"
    else:
        reasons.append(f"You're in the {fed_rate*100:.0f}% federal bracket — tax savings now are valuable")
        recommendation = "TRADITIONAL"
    
    # State tax
    state_name = state_info.get("name", state)
    if state_rate == 0:
        reasons.append(f"{state_name} has no state income tax — no state tax savings from Traditional")
        if recommendation != "TRADITIONAL":
            recommendation = "ROTH"
    elif state_rate >= 0.07:
        reasons.append(f"{state_name} has a high tax rate ({state_rate*100:.1f}%) — Traditional saves more")
        if fed_rate >= 0.22:
            recommendation = "TRADITIONAL"
    
    # Expected retirement rate comparison
    if expected_retirement_rate is not None:
        if expected_retirement_rate > combined_rate:
            reasons.append(f"Expected retirement rate ({expected_retirement_rate*100:.0f}%) > current ({combined_rate*100:.1f}%)")
            recommendation = "ROTH"
        elif expected_retirement_rate < combined_rate:
            reasons.append(f"Expected retirement rate ({expected_retirement_rate*100:.0f}%) < current ({combined_rate*100:.1f}%)")
            recommendation = "TRADITIONAL"
    
    # Tax rate sunset note
    if fed_rate <= 0.12:
        reasons.append("Current low rates may change — lock in with Roth")
    
    return {
        "choice": recommendation,
        "reasons": reasons
    }


# ====================
# DISPLAY FUNCTIONS
# ====================

def print_analysis(results):
    """Pretty print the analysis results."""
    
    print("\n" + "="*60)
    print("TAX CONTRIBUTION ANALYSIS")
    print(f"Data Year: {results['data_year']} | Updated: {results['last_updated'][:10]}")
    print("="*60)
    
    print(f"\n📊 INCOME SUMMARY")
    print(f"   Gross Income:        ${results['gross_income']:,.2f}")
    print(f"   Standard Deduction:  ${results['standard_deduction']:,.2f}")
    print(f"   Taxable Income:      ${results['taxable_income']:,.2f}")
    
    print(f"\n💰 TAX RATES")
    print(f"   Federal Marginal:    {results['federal_marginal_rate']*100:.1f}%")
    print(f"   State Rate:          {results['state_rate']*100:.1f}%")
    print(f"   Combined Marginal:   {results['combined_marginal_rate']*100:.1f}%")
    
    print(f"\n📋 ESTIMATED TAXES")
    print(f"   Federal Tax:         ${results['federal_tax']:,.2f}")
    print(f"   State Tax:           ${results['state_tax']:,.2f}")
    print(f"   Total Tax:           ${results['total_tax']:,.2f}")
    
    print(f"\n🏦 CONTRIBUTION LIMITS ({results['data_year']})")
    print(f"   401(k):              ${results['contribution_limits']['401k']:,}")
    print(f"   IRA:                 ${results['contribution_limits']['ira']:,}")
    
    print(f"\n✨ RECOMMENDATION: {results['recommendation']['choice']}")
    print(f"   Reasons:")
    for reason in results['recommendation']['reasons']:
        print(f"   • {reason}")
    
    print("\n" + "="*60)


# ====================
# MAIN
# ====================

def get_user_input():
    """Get input from user interactively."""
    
    print("\n" + "="*60)
    print("TAX CONTRIBUTION ADVISOR")
    if TAX_DATA:
        print(f"Data: {TAX_DATA.get('data_year', 2025)} | Source: Tax Foundation + IRS")
    print("="*60)
    
    # Income
    while True:
        try:
            income = float(input("\nEnter your gross annual income: $"))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # State
    valid_states = get_all_states()
    while True:
        state = input("Enter your state (2-letter code, e.g., WA, CA, TX): ").upper()
        if state in valid_states:
            break
        print(f"State '{state}' not recognized. Please enter a valid 2-letter state code.")
    
    # Filing status
    print("\nFiling status options:")
    print("  1. Single")
    print("  2. Married filing jointly")
    print("  3. Head of household")
    
    while True:
        choice = input("Select filing status (1-3): ")
        if choice == "1":
            filing_status = "single"
            break
        elif choice == "2":
            filing_status = "married"
            break
        elif choice == "3":
            filing_status = "head_of_household"
            break
        print("Please enter 1, 2, or 3.")
    
    # Age
    while True:
        try:
            age = int(input("\nEnter your age: "))
            break
        except ValueError:
            print("Please enter a valid number.")
    
    # Expected retirement rate (optional)
    retirement_input = input("\nExpected tax rate in retirement (optional, press Enter to skip): ")
    expected_retirement_rate = None
    if retirement_input:
        try:
            expected_retirement_rate = float(retirement_input.replace("%", "")) / 100
        except ValueError:
            print("Invalid input, skipping retirement rate.")
    
    return income, state, filing_status, age, expected_retirement_rate


def main():
    """Main entry point."""
    
    # Get user input
    income, state, filing_status, age, expected_retirement_rate = get_user_input()
    
    # Run analysis
    results = analyze_contribution(
        gross_income=income,
        state=state,
        filing_status=filing_status,
        age=age,
        expected_retirement_rate=expected_retirement_rate
    )
    
    # Display results
    print_analysis(results)
    
    # Option to run again
    again = input("\nRun another analysis? (y/n): ")
    if again.lower() == 'y':
        main()


if __name__ == "__main__":
    main()
