-- Creating a table for authentication information
CREATE TABLE IF NOT EXISTS authentication_info (
    id SERIAL PRIMARY KEY,
    principal_email VARCHAR(255) NOT NULL
);

-- Creating a table for authorisation information
CREATE TABLE IF NOT EXISTS authorization_info (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(255),
    permission VARCHAR(255),
    granted BOOLEAN,
    service VARCHAR(255),
    name VARCHAR(255)
);

-- linking table for multiple log authorisations
CREATE TABLE IF NOT EXISTS audit_log_authorization (
    audit_log_id INTEGER REFERENCES audit_logs(id),
    authorization_info_id INTEGER REFERENCES authorization_info(id),
    PRIMARY KEY (audit_log_id, authorization_info_id)
);

-- Updating the audit_logs table
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    insert_id VARCHAR(255) NOT NULL,
    log_name VARCHAR(255) NOT NULL,
    audit_type VARCHAR(255),
    auth_info_id INTEGER REFERENCES authentication_info(id), -- Foreign key to authentication_info table
    method_name VARCHAR(255),
    request JSONB,
    request_metadata JSONB, -- Same as above
    resource_name VARCHAR(255),
    service_name VARCHAR(255),
    status JSONB, -- Same as above
    -- Removed the JSONB fields that are now represented as foreign keys
    -- The 'principal_email' field is now part of the 'authentication_info' table
    -- Removed redundant fields from this table
);
