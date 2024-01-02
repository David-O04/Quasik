CREATE TABLE IF NOT EXISTS audit_logs (
    insert_id VARCHAR(255),
    log_name VARCHAR(255),
    audit_type VARCHAR(255),
    authentication_info JSONB,
    authorization_info JSONB[],
    method_name VARCHAR(255),
    request JSONB,
    request_metadata JSONB,
    resource_name VARCHAR(255),
    service_name VARCHAR(255),
    status JSONB,
    principal_email VARCHAR(255)  
);
