"""
Clariva SaaS — Synthetic Data Generator
Generates realistic raw data for the analytics platform.
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random
import os

fake = Faker('en_US')
Faker.seed(42)
np.random.seed(42)
random.seed(42)

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────
NUM_ACCOUNTS = 500
NUM_USERS = 2000
NUM_EVENTS = 500_000
NUM_SUBSCRIPTIONS = 600
NUM_INVOICES = 3_000
NUM_TICKETS = 2_500
PLANS = {
'starter': 49,
'growth': 149,
'enterprise': 499
}
REGIONS = ['APAC', 'EMEA', 'NAM', 'LATAM']
INDUSTRIES = ['Technology', 'Finance', 'Healthcare', 'Education', 'Retail', 'Manufacturing', 'Media']
TICKET_CATEGORIES = ['billing', 'technical', 'feature_request', 'onboarding']
TICKET_PRIORITIES = ['low', 'medium', 'high', 'critical']
EVENT_TYPES = ['login', 'page_view', 'feature_used', 'export', 'invite_sent']
ROLES = ['admin', 'member', 'viewer']
TICKET_STATUSES = ['open', 'in_progress', 'resolved', 'closed']

# ──────────────────────────────────────────────
# 1. Generate Accounts
# ──────────────────────────────────────────────
def generate_accounts(n=NUM_ACCOUNTS):
    accounts = []
    for i in range(1, n + 1):
        tier = random.choices(
            ['starter', 'growth', 'enterprise'],
            weights=[0.50, 0.35, 0.15]
        )[0]
        created_at = fake.date_time_between(
            start_date='-36m', end_date='-1m'
        )
    accounts.append({
    'account_id': i,
    'name': fake.company(),
    'industry': random.choice(INDUSTRIES),
    'region': random.choice(REGIONS),
    'csm_owner': fake.name(),
    'created_at': created_at,
    'tier': tier
    })
    return pd.DataFrame(accounts)

# ──────────────────────────────────────────────
# 2. Generate Users
# ──────────────────────────────────────────────
def generate_users(n=NUM_USERS, accounts_df=None):
    users = []
    for i in range(1, n + 1):
        account_id = random.randint(1, NUM_ACCOUNTS)
        # Skew user creation toward last 18 months (growth phase)
        created_at = fake.date_time_between(
            start_date='-36m', end_date='now'
        ) if random.random() > 0.3 else fake.date_time_between(
        start_date='-18m', end_date='now'
        )
        is_active = random.random() > 0.10 # 90% active
        is_active = random.random() > 0.10 # 90% active
        users.append({
        'user_id': i,
        'email': fake.unique.email(),
        'name': fake.name(),
        'account_id': account_id,
        'created_at': created_at,
        'role': random.choices(ROLES, weights=[0.15, 0.65, 0.20])[0],
        'is_active': is_active
    })
    return pd.DataFrame(users)

# ──────────────────────────────────────────────
# 3. Generate Events (with realistic session clusters)
# ──────────────────────────────────────────────
def generate_events(n=NUM_EVENTS, users_df=None):
    events = []
    event_id = 1
    # Create sessions: each user has 10–50 sessions
    active_users = users_df[users_df['is_active'] == True]['user_id'].tolist()
    sessions_per_user = np.random.poisson(lam=25, size=len(active_users))
    session_id_counter = 1
    for user_idx, user_id in enumerate(active_users):
        num_sessions = min(sessions_per_user[user_idx], 60)
        for _ in range(num_sessions):
            session_start = fake.date_time_between(
            start_date='-12m', end_date='now'
            )
            # Each session has 5–15 events
            num_events_in_session = random.randint(5, 15)
            for evt_offset in range(num_events_in_session):
                occurred_at = session_start + timedelta(
                    minutes=evt_offset * random.randint(1, 10)
                )
                event_type = random.choices(
                    EVENT_TYPES,
                    weights=[0.15, 0.40, 0.25, 0.12, 0.08]
                )[0]
                properties = {'page': fake.random_element(['dashboard', 'projects', 'settings', 'reports', 'team'])}
                events.append({
                    'event_id': event_id,
                    'user_id': user_id,
                    'event_type': event_type,
                    'properties': str(properties),
                    'occurred_at': occurred_at,
                    'session_id': session_id_counter
                })
                event_id += 1
            session_id_counter += 1
            if event_id > n:
                break
        if event_id > n:
            break
    return pd.DataFrame(events[:n])

# ──────────────────────────────────────────────
# 4. Generate Subscriptions
# ──────────────────────────────────────────────

def generate_subscriptions(n=NUM_SUBSCRIPTIONS, accounts_df=None):
    subscriptions = []
    used_accounts = set()
    used_accounts = set()
    for i in range(1, n + 1):
        # Some accounts have multiple subscriptions (upgrades)
        account_id = random.randint(1, NUM_ACCOUNTS)
        plan_name = random.choices(
            list(PLANS.keys()),
            weights=[0.45, 0.38, 0.17]
        )[0]
        mrr = PLANS[plan_name]
        status = random.choices(
            ['active', 'cancelled', 'paused'],
            weights=[0.75, 0.15, 0.10] # ~15% churn
        )[0]
        started_at = fake.date_time_between(start_date='-36m', end_date='-3m')
        ended_at = None
        if status in ['cancelled', 'paused']:
            ended_at = fake.date_time_between(
                start_date=started_at + timedelta(days=30),
                end_date='now'
                )
        subscriptions.append({
            'subscription_id': i,
            'account_id': account_id,
            'plan_name': plan_name,
            'status': status,
            'mrr': mrr,
            'started_at': started_at,
            'ended_at': ended_at
        })
    return pd.DataFrame(subscriptions)

# ──────────────────────────────────────────────
# 5. Generate Invoices (with intentional duplicates)
# ──────────────────────────────────────────────
def generate_invoices(n=NUM_INVOICES, subscriptions_df=None):
    invoices = []
    invoice_id = 1
    active_subs = subscriptions_df[subscriptions_df['status'] == 'active']
    for _, sub in active_subs.iterrows():
    # Generate monthly invoices for each active subscription
        start = sub['started_at']
        months_active = min(36, max(1, (datetime.now() - start).days // 30))
        for month_offset in range(months_active):
            issued_at = start + timedelta(days=30 * month_offset)
            if issued_at > datetime.now():
                break
            status = random.choices(
                ['paid', 'pending', 'failed', 'refunded'],
                weights=[0.82, 0.10, 0.05, 0.03]
                )[0]
            paid_at = issued_at + timedelta(days=random.randint(1, 15)) if status == 'paid' else None
            invoices.append({
            'invoice_id': invoice_id,
            'subscription_id': sub['subscription_id'],
            'account_id': sub['account_id'],
            'account_id': sub['account_id'],
            'amount': sub['mrr'],
            'status': status,
            'issued_at': issued_at,
            'paid_at': paid_at
            })
            invoice_id += 1
            # Intentionally duplicate ~2% of invoices to create a problem for dbt to fix
            if random.random() < 0.02:
                invoices.append({
                    'invoice_id': invoice_id - 1, # Duplicate invoice_id
                    'subscription_id': sub['subscription_id'],
                    'account_id': sub['account_id'],
                    'amount': sub['mrr'],
                    'status': 'paid',
                    'issued_at': issued_at + timedelta(hours=2),
                    'paid_at': paid_at + timedelta(hours=3) if paid_at else None
                    })
    return pd.DataFrame(invoices[:n])

# ──────────────────────────────────────────────
# 6. Generate Support Tickets
# ──────────────────────────────────────────────
def generate_tickets(n=NUM_TICKETS, accounts_df=None):
    tickets = []
    for i in range(1, n + 1):
        account_id = random.randint(1, NUM_ACCOUNTS)
        category = random.choice(TICKET_CATEGORIES)
        priority = random.choices(
            TICKET_PRIORITIES,
            weights=[0.25, 0.40, 0.25, 0.10]
            )[0]
        created_at = fake.date_time_between(start_date='-24m', end_date='now')
        status = random.choices(
                TICKET_STATUSES,
                weights=[0.10, 0.15, 0.55, 0.20]
                )[0]
        resolved_at = None
        csat_score = None
        if status in ['resolved', 'closed']:
            # Resolution time varies by priority
            hours_to_resolve = {
                'low': random.randint(24, 168),
                'medium': random.randint(8, 72),
                'high': random.randint(2, 24),
                'critical': random.randint(1, 8)
                }[priority]
            resolved_at = created_at + timedelta(hours=hours_to_resolve)
            csat_score = random.choices(
                [1, 2, 3, 4, 5],
                weights=[0.05, 0.10, 0.20, 0.35, 0.30]
                )[0]
        tickets.append({
            'ticket_id': i,
            'account_id': account_id,
            'subject': fake.sentence(nb_words=6),
            'category': category,
            'status': status,
            'priority': priority,
            'created_at': created_at,
            'resolved_at': resolved_at,
            'csat_score': csat_score
            })
    return pd.DataFrame(tickets)

# ──────────────────────────────────────────────
# Main Execution
# ──────────────────────────────────────────────
if __name__ == '__main__':
    print("Generating Clariva SaaS synthetic data...")
    print("=" * 50)
    print(f" Generating {NUM_ACCOUNTS} accounts...")
    accounts_df = generate_accounts()
    print(f" Generating {NUM_USERS} users...")
    users_df = generate_users(accounts_df=accounts_df)
    print(f" Generating ~{NUM_EVENTS} events (this may take a moment)...")
    events_df = generate_events(users_df=users_df)
    print(f" Generating {NUM_SUBSCRIPTIONS} subscriptions...")
    subscriptions_df = generate_subscriptions(accounts_df=accounts_df)
    print(f" Generating ~{NUM_INVOICES} invoices...")
    invoices_df = generate_invoices(subscriptions_df=subscriptions_df)
    print(f" Generating {NUM_TICKETS} support tickets...")
    tickets_df = generate_tickets(accounts_df=accounts_df)
    
    # Save to CSV files for inspection and backup
    os.makedirs('etl/data', exist_ok=True)
    accounts_df.to_csv('etl/data/raw_accounts.csv', index=False)
    users_df.to_csv('etl/data/raw_users.csv', index=False)
    events_df.to_csv('etl/data/raw_events.csv', index=False)
    subscriptions_df.to_csv('etl/data/raw_subscriptions.csv', index=False)
    invoices_df.to_csv('etl/data/raw_invoices.csv', index=False)
    tickets_df.to_csv('etl/data/raw_support_tickets.csv', index=False)

    print("\n" + "=" * 50)
    print("Data generation complete!")
    print(f" Accounts: {len(accounts_df):>8,} rows")
    print(f" Users: {len(users_df):>8,} rows")
    print(f" Events: {len(events_df):>8,} rows")
    print(f" Subscriptions: {len(subscriptions_df):>8,} rows")
    print(f" Invoices: {len(invoices_df):>8,} rows")
    print(f" Tickets: {len(tickets_df):>8,} rows")
    print(f"\nCSV files saved to etl/data/")