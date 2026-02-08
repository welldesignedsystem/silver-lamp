```bash
docker run -v $(pwd):/data plantuml/plantuml -tsvg classes_grouped.puml
```
```bash
docker run -v $(pwd):/data plantuml/plantuml -tsvg classes_original.puml
```

## Telecom Company
```sql
-- Telecom Balance Maintenance Database Schema
-- Simplified schema with only accounts, transactions, and PRN tables

-- ============================================
-- TRANSACTIONS TABLE
-- ============================================
CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_type ENUM('credit', 'debit', 'refund', 'adjustment') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    balance_before DECIMAL(10, 2) NOT NULL,
    balance_after DECIMAL(10, 2) NOT NULL,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR(255),
    prn_id INT NULL,
    status ENUM('pending', 'completed', 'failed') DEFAULT 'completed',
    FOREIGN KEY (prn_id) REFERENCES prn(prn_id),
    INDEX idx_account (account_id),
    INDEX idx_date (transaction_date),
    INDEX idx_prn (prn_id)
);

-- ============================================
-- PRN (Payment Reference Number) TABLE
-- ============================================
CREATE TABLE prn (
    prn_id INT PRIMARY KEY AUTO_INCREMENT,
    prn_number VARCHAR(50) UNIQUE NOT NULL,
    account_id INT NOT NULL,
    status ENUM('pending', 'paid', 'expired', 'cancelled') DEFAULT 'pending',
    FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
    INDEX idx_prn_number (prn_number),
    INDEX idx_account (account_id),
    INDEX idx_status (status)
);

```
