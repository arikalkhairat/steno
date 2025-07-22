# Step-by-Step Enhancement: Document Security & Key Authentication

## 🔒 **Project Security Enhancement Goal**
Add cryptographic security layer to the QR Code Watermarking Tool where each document gets a unique security key, and only QR codes generated with that specific key can be used for that document. This prevents unauthorized watermarking and ensures document authenticity.

---

## **STEP 1: Create Security Module Backend**
**File to create:** `security_utils.py`

### **Prompt for Step 1:**
```
I want to create a new file called "security_utils.py" for my QR watermarking project to handle document security and key authentication.

Please create this new Python file with these functions:

1. `generate_document_key(document_path: str, additional_data: str = "")` - Generate unique key based on document content hash + timestamp
2. `encrypt_qr_data(qr_text: str, document_key: str)` - Encrypt QR text using AES encryption with document key
3. `decrypt_qr_data(encrypted_data: str, document_key: str)` - Decrypt QR text using document key
4. `create_key_signature(document_key: str, document_hash: str)` - Create digital signature for key validation
5. `verify_key_signature(document_key: str, signature: str, document_hash: str)` - Verify if key belongs to document
6. `generate_document_hash(document_path: str)` - Create SHA-256 hash of document content
7. `is_qr_authorized_for_document(qr_data: str, document_key: str, document_path: str)` - Validate QR-document pairing

Use these libraries: hashlib, hmac, secrets, cryptography (Fernet), base64
Include comprehensive error handling and detailed docstrings.
```

**Expected output:** New `security_utils.py` file with cryptographic security functions

---

## **STEP 2: Update Requirements for Security Libraries**
**File to modify:** `requirements.txt`

### **Prompt for Step 2:**
```
I need to update my requirements.txt file to include the new security libraries needed for document authentication and encryption.

Please add these new dependencies to the existing requirements.txt:

- cryptography>=3.4.8 (for AES encryption/decryption)
- pyotp>=2.6.0 (for time-based tokens if needed)
- bcrypt>=3.2.0 (for password hashing)

Keep all existing dependencies intact, just append the new security-related ones.
```

**Expected output:** Updated `requirements.txt` with security dependencies

---

## **STEP 3: Enhance QR Utils with Security Integration**
**File to modify:** `qr_utils.py`

### **Prompt for Step 3:**
```
I need to enhance my existing qr_utils.py file to integrate with the new security system.

Please add these new functions while keeping all existing functions unchanged:

1. `generate_secure_qr(data: str, document_key: str, output_path: str)` - Generate QR with encrypted data
2. `read_secure_qr(image_path: str, document_key: str)` - Read and decrypt QR data using document key
3. `embed_security_metadata(qr_data: str, document_key: str, timestamp: str)` - Add security metadata to QR
4. `extract_security_metadata(qr_data: str)` - Extract security info from QR data
5. `validate_qr_security(qr_data: str, document_key: str, document_hash: str)` - Validate QR security

The functions should use the security_utils module for encryption/decryption.
Import the security_utils at the top of the file.
```

**Expected output:** Enhanced `qr_utils.py` with security integration

---

## **STEP 4: Add Security to Main Processing Logic**
**File to modify:** `main.py`

### **Prompt for Step 4:**
```
I want to enhance main.py to support document security and key-based QR generation.

Please modify these existing functions and add new ones:

1. Update `generate_qr_code()` to accept `--secure` flag and `--document-path` parameter for secure QR generation
2. Add `generate_document_key_command()` - CLI command to generate and display document security key
3. Add `validate_qr_document_pair()` - CLI command to validate if QR belongs to specific document
4. Update `embed_watermark_to_docx()` and `embed_watermark_to_pdf()` to validate QR security before embedding
5. Update `extract_watermark_from_docx()` and `extract_watermark_from_pdf()` to include security validation in extraction

Add new argument parser commands:
- `generate_key` - Generate security key for document
- `validate_security` - Validate QR-document security pairing

Keep all existing functionality working, just add security as optional enhanced features.
```

**Expected output:** Enhanced `main.py` with security commands and validation

---

## **STEP 5: Add Security API Endpoints**
**File to modify:** `app.py`

### **Prompt for Step 5:**
```
I need to add new security-related API endpoints to app.py for document key management and secure QR operations.

Please add these new routes while keeping all existing routes unchanged:

1. `/generate_document_key` (POST) - Generate unique security key for uploaded document
2. `/generate_secure_qr` (POST) - Generate QR with encryption using document key
3. `/validate_qr_security` (POST) - Validate if QR belongs to specific document
4. `/get_document_hash` (POST) - Get document hash for security verification
5. `/embed_secure_document` (POST) - Enhanced embed with security validation

Also modify existing routes:
- Update `/embed_document` to include optional security validation
- Update `/extract_document` to include security verification in extraction results

Add proper error handling for security failures (wrong key, unauthorized QR, etc.).
Include security status in all JSON responses.
```

**Expected output:** Enhanced `app.py` with security API endpoints

---

## **STEP 6: Add Security Tab to Frontend**
**File to modify:** `templates/index.html`

### **Prompt for Step 6:**
```
I want to add a new "Document Security" tab to my existing 4-tab interface (Generate QR, QR Configuration, Embed Watermark, Validate Document).

Please add:
1. A new tab button "Document Security" in the tab-navigation section
2. A new tab-pane with id "security-tab" containing:
   - File upload for document to secure
   - "Generate Security Key" button
   - Display area for generated key (with copy button)
   - Document hash display
   - Security status indicator
   - "Generate Secure QR" section with:
     * Text input for QR data
     * Document key input field
     * "Generate Secure QR" button
   - "Validate QR-Document Pair" section with:
     * QR file upload
     * Document file upload  
     * Document key input
     * "Validate Security" button
     * Results display area

Keep all existing 4 tabs exactly as they are. Use the same modern styling and color scheme.
```

**Expected output:** Enhanced `templates/index.html` with Document Security tab

---

## **STEP 7: Add Security JavaScript Functions**
**File to modify:** `templates/index.html` (JavaScript section)

### **Prompt for Step 7:**
```
Now I need to add JavaScript functionality for the new Document Security tab in the existing index.html file.

Add these JavaScript functions in the existing <script> section:

1. `generateDocumentKey()` - Call /generate_document_key API and display the key
2. `generateSecureQR()` - Generate encrypted QR using document key
3. `validateQRSecurity()` - Validate QR-document security pairing
4. `copySecurityKey()` - Copy generated key to clipboard
5. `showSecurityStatus(status, message)` - Display security validation results
6. `hashDocument()` - Get document hash for display
7. Update existing tab switching logic to include "security" tab
8. Add security key validation (format checking)

Include proper error handling for security failures and user feedback for security operations.
Maintain the same styling and behavior patterns as existing JavaScript functions.
```

**Expected output:** JavaScript functions for Document Security functionality

---

## **STEP 8: Enhance Embed Tab with Security Options**
**File to modify:** `templates/index.html` (Embed Watermark tab)

### **Prompt for Step 8:**
```
I want to enhance the existing "Embed Watermark" tab to include document security options.

Please modify the embed tab to add:
1. A new expandable "Security Settings" section with:
   - "Enable Document Security" checkbox
   - Document security key input field (auto-populated if document was secured)
   - "Validate QR Authorization" checkbox  
   - Security status display
   - "Generate Key for This Document" button (if no key exists)
2. Update form submission to include security parameters
3. Add security validation before allowing embed process
4. Show security warnings if QR doesn't match document key

Keep all existing embed functionality exactly the same, just add these as optional security enhancements that are disabled by default.
```

**Expected output:** Enhanced Embed tab with security options

---

## **STEP 9: Add Security to Validation Process**
**File to modify:** `templates/index.html` (Validate Document tab)

### **Prompt for Step 9:**
```
I need to enhance the existing "Validate Document" tab to include security verification.

Please modify the validate tab to add:
1. "Advanced Security Validation" expandable section with:
   - Document security key input field
   - "Verify Document Authenticity" checkbox
   - "Check QR Authorization" checkbox
   - Security validation results display
2. Enhanced results display showing:
   - QR extraction status
   - Security verification status  
   - Key authorization status
   - Document integrity status
3. Color-coded security indicators (green=secure, yellow=warning, red=unauthorized)

Keep the existing basic validation working exactly as before, just add enhanced security validation as optional advanced feature.
```

**Expected output:** Enhanced Validate tab with security verification

---

## **STEP 10: Update Backend Security Processing**
**File to modify:** `app.py` (embed and extract routes)

### **Prompt for Step 10:**
```
Now I need to update the existing embed_document_route() and extract_document_route() functions in app.py to handle security validation.

Please modify:

For embed_document_route():
1. Check if security is enabled from form data
2. If enabled, validate QR authorization for the document
3. Generate document key if not provided
4. Encrypt QR data before embedding if security is enabled
5. Add security metadata to the response

For extract_document_route():
1. Extract and decrypt QR data if security was used
2. Validate QR authorization against document
3. Verify document integrity
4. Include security status in extraction results
5. Show security warnings for unauthorized QRs

Maintain full backward compatibility - all existing functionality should work exactly the same when security is not enabled.
```

**Expected output:** Enhanced embed and extract functions with security processing

---

## **STEP 11: Add Security to LSB Steganography**
**File to modify:** `lsb_steganography.py`

### **Prompt for Step 11:**
```
I need to enhance the LSB steganography functions to handle encrypted QR data and security metadata.

Please add these new functions while keeping all existing functions unchanged:

1. `embed_secure_qr_to_image(cover_path: str, encrypted_qr_data: str, key_hash: str, output_path: str)` - Embed encrypted QR with security header
2. `extract_secure_qr_from_image(stego_path: str, document_key: str, output_path: str)` - Extract and decrypt secure QR
3. `add_security_header(qr_bits: str, key_hash: str, timestamp: str)` - Add security metadata to QR bit stream
4. `parse_security_header(extracted_bits: str)` - Extract security metadata from bit stream  
5. `validate_embedded_security(extracted_header: dict, document_key: str)` - Validate security metadata

The security header should include: key hash (32 bits), timestamp (32 bits), checksum (16 bits)
Update existing embed/extract functions to optionally use security mode.
```

**Expected output:** Enhanced LSB functions with security capabilities

---

## **STEP 12: Add Security Database/Storage**
**File to create:** `security_storage.py`

### **Prompt for Step 12:**
```
I want to create a simple storage system for document security keys and metadata.

Please create a new file "security_storage.py" with these functions:

1. `init_security_storage()` - Initialize JSON-based storage for security data
2. `store_document_key(document_hash: str, key_data: dict)` - Store document security information  
3. `retrieve_document_key(document_hash: str)` - Get stored security key for document
4. `list_secured_documents()` - List all documents with security keys
5. `delete_document_key(document_hash: str)` - Remove document security data
6. `cleanup_expired_keys(days: int = 30)` - Clean up old security keys
7. `export_security_backup()` - Export security data for backup
8. `import_security_backup(backup_data: str)` - Import security data from backup

Use JSON file storage for simplicity. Include proper file locking and error handling.
Store data in: `security_keys.json` in the project root.
```

**Expected output:** New `security_storage.py` file for key management

---

## **STEP 13: Add Security Management Interface**
**File to modify:** `templates/index.html` (Document Security tab enhancement)

### **Prompt for Step 13:**
```
I want to enhance the Document Security tab to include key management capabilities.

Please add to the existing security tab:
1. "Key Management" section with:
   - List of all secured documents (table format)
   - Document name, hash, key creation date, status
   - Actions: View Key, Delete Key, Export Data
   - Search/filter functionality
2. "Backup & Recovery" section with:
   - Export security keys button
   - Import security keys file upload
   - Cleanup expired keys button (with confirmation)
3. "Security Statistics" dashboard showing:
   - Total secured documents
   - Recent security activities
   - Key usage statistics
   - Security validation success rate

Add proper confirmation dialogs for destructive operations.
Maintain the existing security generation and validation functionality.
```

**Expected output:** Enhanced Document Security tab with key management

---

## **STEP 14: Add Security Logging & Audit**
**File to create:** `security_audit.py`

### **Prompt for Step 14:**
```
I need to create a security audit and logging system to track all security operations.

Please create a new file "security_audit.py" with these functions:

1. `log_security_event(event_type: str, document_hash: str, details: dict)` - Log security events
2. `get_security_log(start_date: str = None, end_date: str = None)` - Retrieve security logs
3. `generate_security_report(document_hash: str = None)` - Generate security audit report
4. `check_security_violations()` - Check for suspicious activities
5. `export_audit_log()` - Export security logs for compliance
6. `cleanup_old_logs(days: int = 90)` - Clean up old audit logs

Track these events:
- Key generation
- QR encryption/decryption
- Security validation attempts
- Unauthorized access attempts
- Key management operations

Use JSON file logging with rotation. Store in: `security_audit.log`
```

**Expected output:** New `security_audit.py` file for security logging

---

## **STEP 15: Update Documentation & Testing**
**File to modify:** `README.md`

### **Prompt for Step 15:**
```
Please update the README.md file to document the new Document Security features.

Add a new major section called "🔒 Document Security & Authentication" that explains:

1. Security Overview - How the key-based authentication works
2. Security Features:
   - Unique document keys
   - QR encryption/decryption
   - Document-QR authorization pairing
   - Security validation and audit logging
3. Security Workflow:
   - Generate document security key
   - Create secure QR codes  
   - Embed with security validation
   - Extract with authentication verification
4. API Security Endpoints documentation
5. Security Best Practices and recommendations
6. Troubleshooting security issues

Also update:
- Feature list to mention 5-tab interface including Document Security
- Installation instructions for new security dependencies
- Add security considerations and warnings
- Examples of secure watermarking scenarios

Keep all existing documentation intact, just add the comprehensive security documentation.
```

**Expected output:** Updated README.md with complete security documentation

---

## **📋 Implementation Checklist**

After completing all steps, you should have:

- [ ] **Step 1**: New `security_utils.py` with cryptographic functions
- [ ] **Step 2**: Updated `requirements.txt` with security libraries
- [ ] **Step 3**: Enhanced `qr_utils.py` with security integration
- [ ] **Step 4**: Updated `main.py` with security CLI commands
- [ ] **Step 5**: Added security API endpoints in `app.py`
- [ ] **Step 6**: New Document Security tab in UI
- [ ] **Step 7**: JavaScript for security functionality
- [ ] **Step 8**: Security options in Embed tab
- [ ] **Step 9**: Security verification in Validate tab
- [ ] **Step 10**: Enhanced backend security processing
- [ ] **Step 11**: Security support in LSB functions
- [ ] **Step 12**: Security key storage system
- [ ] **Step 13**: Key management interface
- [ ] **Step 14**: Security audit and logging
- [ ] **Step 15**: Updated documentation

## **🔒 Expected Security Features**

Your enhanced application will have:

### **Core Security Features:**
- **Unique Document Keys**: Each document gets cryptographically unique key
- **QR Encryption**: AES encryption of QR data using document key
- **Authorization Pairing**: QR codes only work with their specific document
- **Security Validation**: Multi-layer verification during embed/extract

### **User Interface Enhancements:**
- **5 tabs**: Generate QR, QR Config, Embed, Validate, **Document Security**
- **Key Management**: Generate, store, retrieve, delete document keys
- **Security Status**: Real-time security validation indicators
- **Audit Dashboard**: Security events and statistics tracking

### **API Security:**
- **Encrypted Endpoints**: All security operations through secure APIs
- **Key Validation**: Server-side authorization checking
- **Audit Logging**: Complete security event tracking
- **Backup/Recovery**: Security key export/import functionality

## **🛡️ Security Workflow:**

```
1. Upload Document → Generate Security Key → Store Key
2. Create QR Text → Encrypt with Document Key → Generate Secure QR  
3. Upload Document + Secure QR → Validate Authorization → Embed Watermark
4. Upload Watermarked Document + Key → Extract QR → Decrypt & Validate
5. Security Dashboard → View Audit Logs → Manage Keys
```

## **⚠️ Security Considerations:**

- **Key Storage**: Keys stored locally in JSON (consider encryption for production)
- **Transport Security**: Use HTTPS in production for API calls
- **Key Backup**: Regular backup of security keys recommended
- **Audit Compliance**: Complete logging for security audit requirements

This enhancement transforms your watermarking tool into a **enterprise-grade document security system** with full cryptographic protection! 🛡️