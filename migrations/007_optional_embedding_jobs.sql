-- 007_optional_embedding_jobs.sql
-- Optional jobs table to track embedding generation

-- Note: MSSQL does not have a native uuid_generate_v4() equivalent that can be used as a column default.
-- Instead, the UNIQUEIDENTIFIER type is used, and NEWID() or NEWSEQUENTIALID() is typically the default.

CREATE TABLE embedding_jobs (
    -- Use UNIQUEIDENTIFIER for UUID and NEWID() for a random UUID default.
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    
    -- Assuming 'products' table also uses UNIQUEIDENTIFIER for its 'id'
    product_id UNIQUEIDENTIFIER FOREIGN KEY REFERENCES products(id) ON DELETE CASCADE,
    
    status NVARCHAR(50) DEFAULT 'pending', -- pending, in_progress, done, failed (using NVARCHAR instead of TEXT)
    attempts INT DEFAULT 0,
    last_error NVARCHAR(MAX), -- Using NVARCHAR(MAX) instead of TEXT
    
    -- Use DATETIMEOFFSET for timezone-aware data and GETUTCDATE() or SYSDATETIMEOFFSET() for default.
    created_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET(), 
    updated_at DATETIMEOFFSET DEFAULT SYSDATETIMEOFFSET()
);

-- MSSQL uses a different syntax for 'CREATE INDEX IF NOT EXISTS' via conditional logic
-- or simply relies on the CREATE INDEX statement without the IF NOT EXISTS clause.
-- If the migration tool supports it, using the simple CREATE INDEX is often preferred
-- as the tool handles existence checks.

CREATE INDEX embedding_jobs_status_idx ON embedding_jobs (status);