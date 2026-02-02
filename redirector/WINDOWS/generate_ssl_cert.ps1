<#
.SYNOPSIS
    Generate Self-Signed SSL Certificate for Windows Backend API

.DESCRIPTION
    Creates a self-signed TLS certificate for securing the Windows Backend API.
    Supports both development (self-signed) and production (CA-signed) workflows.
    
    Features:
    - SHA-256 signature algorithm
    - RSA 4096-bit key
    - 365-day validity (customizable)
    - Subject Alternative Names (SAN) support
    - Automatic Windows certificate store installation
    - PEM format export for Python compatibility

.PARAMETER CertName
    Common Name (CN) for the certificate. Use your server's hostname or IP.
    Default: "backend-api.local"

.PARAMETER OutputDir
    Directory to save certificate files
    Default: C:\backend_api\certs

.PARAMETER ValidDays
    Certificate validity period in days
    Default: 365

.PARAMETER SANs
    Additional Subject Alternative Names (comma-separated)
    Example: "192.168.1.100,backend.example.com"

.EXAMPLE
    .\generate_ssl_cert.ps1
    Generate certificate with default settings

.EXAMPLE
    .\generate_ssl_cert.ps1 -CertName "192.168.1.100" -ValidDays 730
    Generate certificate for specific IP, valid for 2 years

.EXAMPLE
    .\generate_ssl_cert.ps1 -SANs "192.168.1.100,backend.local,10.0.0.50"
    Generate certificate with multiple SANs

.NOTES
    Version: 1.0.0
    Author: Backend API Team
    Requires: PowerShell 5.1+ running as Administrator
    Compatible: Windows Server 2019/2022, Windows 10/11
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$CertName = "backend-api.local",
    
    [Parameter(Mandatory=$false)]
    [string]$OutputDir = "C:\backend_api\certs",
    
    [Parameter(Mandatory=$false)]
    [int]$ValidDays = 365,
    
    [Parameter(Mandatory=$false)]
    [string]$SANs = ""
)

# ═══════════════════════════════════════════════════════════════════════════
# SETUP AND VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "║     SSL CERTIFICATE GENERATOR FOR WINDOWS BACKEND API v4.0.3           ║" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "❌ ERROR: This script must run as Administrator" -ForegroundColor Red
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    exit 1
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "✅ Created directory: $OutputDir" -ForegroundColor Green
}

# ═══════════════════════════════════════════════════════════════════════════
# BUILD SUBJECT ALTERNATIVE NAMES (SAN)
# ═══════════════════════════════════════════════════════════════════════════

$SANList = @($CertName)
if ($SANs) {
    $SANList += $SANs -split ','
}
$SANList = $SANList | ForEach-Object { $_.Trim() } | Sort-Object -Unique

Write-Host "[1/7] Certificate Configuration" -ForegroundColor Yellow
Write-Host "   Common Name (CN): $CertName" -ForegroundColor Cyan
Write-Host "   Subject Alternative Names:" -ForegroundColor Cyan
foreach ($san in $SANList) {
    Write-Host "     - $san" -ForegroundColor Cyan
}
Write-Host "   Validity: $ValidDays days" -ForegroundColor Cyan
Write-Host "   Algorithm: RSA 4096-bit, SHA-256" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE SELF-SIGNED CERTIFICATE
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[2/7] Generating self-signed certificate..." -ForegroundColor Yellow

# Build SAN extension
$SANExtension = $SANList | ForEach-Object {
    if ($_ -match '^\d+\.\d+\.\d+\.\d+$') {
        "IPAddress=$_"
    } else {
        "DNS=$_"
    }
}
$SANString = $SANExtension -join '&'

try {
    # Create certificate with SAN
    $cert = New-SelfSignedCertificate `
        -Subject "CN=$CertName" `
        -DnsName $SANList `
        -CertStoreLocation "Cert:\LocalMachine\My" `
        -KeyAlgorithm RSA `
        -KeyLength 4096 `
        -HashAlgorithm SHA256 `
        -NotAfter (Get-Date).AddDays($ValidDays) `
        -KeyUsage DigitalSignature, KeyEncipherment `
        -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1") `
        -FriendlyName "Backend API TLS Certificate"
    
    Write-Host "   ✅ Certificate generated successfully" -ForegroundColor Green
    Write-Host "   Thumbprint: $($cert.Thumbprint)" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "   ❌ Failed to generate certificate: $_" -ForegroundColor Red
    exit 1
}

# ═══════════════════════════════════════════════════════════════════════════
# EXPORT TO PFX FORMAT (WITH PRIVATE KEY)
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[3/7] Exporting to PFX format..." -ForegroundColor Yellow

$pfxPassword = ConvertTo-SecureString -String (New-Guid).ToString() -Force -AsPlainText
$pfxPath = Join-Path $OutputDir "backend_api.pfx"

try {
    Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $pfxPassword | Out-Null
    Write-Host "   ✅ Exported to: $pfxPath" -ForegroundColor Green
    Write-Host "   ⚠️  PFX Password saved to: $OutputDir\pfx_password.txt" -ForegroundColor Yellow
    
    # Save password to file (secure this file!)
    $pfxPassword | ConvertFrom-SecureString | Out-File (Join-Path $OutputDir "pfx_password.txt")
    Write-Host ""
} catch {
    Write-Host "   ❌ Failed to export PFX: $_" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════════════════
# EXPORT TO PEM FORMAT (FOR PYTHON)
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[4/7] Exporting to PEM format (for Python)..." -ForegroundColor Yellow

$certPath = Join-Path $OutputDir "backend_api_cert.pem"
$keyPath = Join-Path $OutputDir "backend_api_key.pem"

try {
    # Export certificate (public key)
    $certBytes = $cert.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert)
    $certPem = "-----BEGIN CERTIFICATE-----`n"
    $certPem += [System.Convert]::ToBase64String($certBytes, [System.Base64FormattingOptions]::InsertLineBreaks)
    $certPem += "`n-----END CERTIFICATE-----"
    $certPem | Out-File -FilePath $certPath -Encoding ASCII
    Write-Host "   ✅ Certificate exported to: $certPath" -ForegroundColor Green
    
    # For private key, we need to use certutil or openssl
    # Windows doesn't directly export private keys to PEM
    Write-Host "   ℹ️  To export private key, use one of these methods:" -ForegroundColor Cyan
    Write-Host "   "
    Write-Host "   Method 1: Using OpenSSL (if installed)" -ForegroundColor Gray
    Write-Host "   openssl pkcs12 -in $pfxPath -nocerts -out $keyPath -nodes" -ForegroundColor Gray
    Write-Host "   "
    Write-Host "   Method 2: Using certutil" -ForegroundColor Gray
    Write-Host "   certutil -exportPFX -p `"PFX_PASSWORD`" my $($cert.Thumbprint) $pfxPath NoRoot" -ForegroundColor Gray
    Write-Host ""
    
    # For now, create a combined PEM file with just the certificate
    # Users will need to add the private key manually or use PFX
    Write-Host "   ⚠️  IMPORTANT: For full PEM support, extract private key using OpenSSL" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "   ❌ Failed to export PEM: $_" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════════════════
# INSTALL TO TRUSTED ROOT (OPTIONAL)
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[5/7] Installing to Trusted Root Certificate Authorities..." -ForegroundColor Yellow

$installToRoot = Read-Host "   Install to Trusted Root? (Y/N) [Default: N]"
if ($installToRoot -eq 'Y' -or $installToRoot -eq 'y') {
    try {
        # Export certificate
        $store = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "LocalMachine")
        $store.Open("ReadWrite")
        $store.Add($cert)
        $store.Close()
        
        Write-Host "   ✅ Certificate installed to Trusted Root CA" -ForegroundColor Green
        Write-Host "   ⚠️  WARNING: This is for development only. Don't do this in production." -ForegroundColor Yellow
    } catch {
        Write-Host "   ❌ Failed to install to Trusted Root: $_" -ForegroundColor Red
    }
} else {
    Write-Host "   ⏭️  Skipped installation to Trusted Root" -ForegroundColor Gray
}
Write-Host ""

# ═══════════════════════════════════════════════════════════════════════════
# SET FILE PERMISSIONS
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[6/7] Securing certificate files..." -ForegroundColor Yellow

try {
    # Get current user
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    
    # Set restrictive permissions on certificate files
    Get-ChildItem $OutputDir -File | ForEach-Object {
        $acl = Get-Acl $_.FullName
        
        # Disable inheritance
        $acl.SetAccessRuleProtection($true, $false)
        
        # Remove all existing rules
        $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) | Out-Null }
        
        # Add current user and SYSTEM
        $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule(
            $currentUser, "FullControl", "Allow"
        )))
        $acl.AddAccessRule((New-Object System.Security.AccessControl.FileSystemAccessRule(
            "SYSTEM", "FullControl", "Allow"
        )))
        
        Set-Acl $_.FullName $acl
    }
    
    Write-Host "   ✅ File permissions secured" -ForegroundColor Green
    Write-Host "   Owner: $currentUser + SYSTEM only" -ForegroundColor Cyan
    Write-Host ""
} catch {
    Write-Host "   ⚠️  Failed to set permissions: $_" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════════════════
# GENERATE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

Write-Host "[7/7] Generating summary..." -ForegroundColor Yellow
Write-Host ""

$summary = @"
═══════════════════════════════════════════════════════════════════════════
SSL CERTIFICATE GENERATION COMPLETE
═══════════════════════════════════════════════════════════════════════════

Certificate Details:
  Common Name: $CertName
  Thumbprint: $($cert.Thumbprint)
  Valid From: $($cert.NotBefore)
  Valid Until: $($cert.NotAfter)
  Algorithm: RSA 4096-bit, SHA-256
  
Subject Alternative Names:
$($SANList | ForEach-Object { "  - $_" } | Out-String)

Generated Files:
  📄 Certificate (PEM): $certPath
  🔑 Private Key (PEM): $keyPath (manual extraction required)
  📦 PFX Bundle: $pfxPath
  🔐 PFX Password: $OutputDir\pfx_password.txt

Windows Certificate Store:
  Location: Cert:\LocalMachine\My\$($cert.Thumbprint)
  Friendly Name: Backend API TLS Certificate

═══════════════════════════════════════════════════════════════════════════
NEXT STEPS
═══════════════════════════════════════════════════════════════════════════

1. EXTRACT PRIVATE KEY (Required for Python):
   
   Using OpenSSL:
   openssl pkcs12 -in $pfxPath -nocerts -out $keyPath -nodes
   # Password is in: $OutputDir\pfx_password.txt
   
2. UPDATE config.env:
   
   ENABLE_HTTPS=true
   SSL_CERT_PATH=$certPath
   SSL_KEY_PATH=$keyPath
   SSL_PORT=6922
   
3. TEST LOCALLY:
   
   # Start backend with HTTPS
   python backend_api_v4_https.py
   
   # Test from Windows
   curl -k https://localhost:6922/health
   
4. CONFIGURE VPS L4 REDIRECTOR:
   
   Update /etc/l4-redirector/config.env:
   LOCALTONET_IP=YOUR_WINDOWS_IP
   LOCALTONET_PORT=6922  # HTTPS port
   BACKEND_USE_HTTPS=true
   BACKEND_VERIFY_SSL=false  # For self-signed certs
   
5. TEST FROM VPS:
   
   curl -k -H "Authorization: Bearer YOUR_TOKEN" \
        https://YOUR_WINDOWS_IP:6922/connections \
        -d '{"test": "data"}' \
        -H "Content-Type: application/json"

═══════════════════════════════════════════════════════════════════════════
SECURITY NOTES
═══════════════════════════════════════════════════════════════════════════

⚠️  SELF-SIGNED CERTIFICATE LIMITATIONS:
   - Not trusted by browsers/clients by default
   - Must use -k/--insecure flag with curl
   - Set BACKEND_VERIFY_SSL=false on VPS
   - Consider getting CA-signed certificate for production

🔒 PROTECT THESE FILES:
   - $keyPath (private key)
   - $pfxPath (contains private key)
   - $OutputDir\pfx_password.txt (PFX password)
   
   DO NOT commit these to version control!
   DO NOT share with unauthorized users!

🔄 CERTIFICATE RENEWAL:
   - This certificate expires on: $($cert.NotAfter)
   - Set reminder to renew 30 days before expiration
   - Run this script again to generate new certificate

📖 FULL DOCUMENTATION:
   See: redirector/WINDOWS/TLS_SETUP_GUIDE.md

═══════════════════════════════════════════════════════════════════════════
"@

Write-Host $summary

# Save summary to file
$summary | Out-File (Join-Path $OutputDir "certificate_summary.txt") -Encoding UTF8

Write-Host "✅ Summary saved to: $OutputDir\certificate_summary.txt" -ForegroundColor Green
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🎉 CERTIFICATE GENERATION COMPLETE!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
