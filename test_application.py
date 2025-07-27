#!/usr/bin/env python3
"""
Comprehensive Test Suite for Steno Watermarking Application
===========================================================

This single test file covers all essential testing needs:
- Backend API endpoints testing
- Image processing functionality
- Security features
- File structure validation
- Error handling

Usage:
    python test_application.py [--test-type all|api|images|security|structure]
"""

import os
import sys
import json
import requests
import time
import argparse
from pathlib import Path
from datetime import datetime


class StenoTestSuite:
    """Comprehensive test suite for the Steno application."""
    
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.test_results = {}
        self.failed_tests = []
        
    def log(self, message, level="INFO"):
        """Log test messages with timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_api_endpoints(self):
        """Test all Flask API endpoints."""
        self.log("🧪 Testing API Endpoints", "TEST")
        
        endpoints_to_test = [
            ("/", "GET", "Main page"),
            ("/generate_qr", "POST", "QR Generation"),
            ("/analyze_qr_text", "POST", "QR Analysis"),
            ("/compare_qr_versions", "POST", "QR Comparison"),
            ("/calculate_qr_capacity", "POST", "QR Capacity"),
            ("/list_documents", "GET", "Document List"),
            ("/api/security/statistics", "GET", "Security Stats"),
        ]
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        for endpoint, method, description in endpoints_to_test:
            try:
                if method == "GET":
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                else:
                    # Basic POST data for testing
                    test_data = {"data": "test", "text": "test"}
                    response = requests.post(f"{self.base_url}{endpoint}", 
                                           data=test_data, timeout=5)
                
                if response.status_code in [200, 400]:  # 400 is OK for missing data
                    self.log(f"✅ {description}: {response.status_code}")
                    results["passed"] += 1
                    results["details"].append(f"✅ {description}: OK")
                else:
                    self.log(f"❌ {description}: {response.status_code}", "ERROR")
                    results["failed"] += 1
                    results["details"].append(f"❌ {description}: {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                self.log(f"❌ {description}: Connection failed", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ {description}: Connection failed")
            except Exception as e:
                self.log(f"❌ {description}: {str(e)}", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ {description}: {str(e)}")
        
        self.test_results["api_endpoints"] = results
        return results["failed"] == 0
    
    def test_file_structure(self):
        """Test essential file and directory structure."""
        self.log("🧪 Testing File Structure", "TEST")
        
        required_files = [
            "app.py",
            "main.py", 
            "lsb_steganography.py",
            "qr_utils.py",
            "security_utils.py",
            "security_storage.py",
            "qr_config_assistant.py",
            "requirements.txt",
            "README.md",
            ".gitignore"
        ]
        
        required_dirs = [
            "static/uploads",
            "static/generated", 
            "public/documents",
            "templates",
            "security_backups"
        ]
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        # Test files
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log(f"✅ File exists: {file_path}")
                results["passed"] += 1
                results["details"].append(f"✅ {file_path}")
            else:
                self.log(f"❌ Missing file: {file_path}", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ Missing: {file_path}")
        
        # Test directories
        for dir_path in required_dirs:
            if os.path.exists(dir_path):
                self.log(f"✅ Directory exists: {dir_path}")
                results["passed"] += 1
                results["details"].append(f"✅ {dir_path}/")
            else:
                self.log(f"❌ Missing directory: {dir_path}", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ Missing: {dir_path}/")
        
        self.test_results["file_structure"] = results
        return results["failed"] == 0
    
    def test_import_functionality(self):
        """Test if all core modules can be imported."""
        self.log("🧪 Testing Module Imports", "TEST")
        
        modules_to_test = [
            "main",
            "lsb_steganography",
            "qr_utils", 
            "security_utils",
            "security_storage",
            "qr_config_assistant"
        ]
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                self.log(f"✅ Successfully imported: {module_name}")
                results["passed"] += 1
                results["details"].append(f"✅ {module_name}")
            except ImportError as e:
                self.log(f"❌ Failed to import {module_name}: {e}", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ {module_name}: {e}")
            except Exception as e:
                self.log(f"❌ Error importing {module_name}: {e}", "ERROR")
                results["failed"] += 1
                results["details"].append(f"❌ {module_name}: {e}")
        
        self.test_results["imports"] = results
        return results["failed"] == 0
    
    def test_security_features(self):
        """Test security-related functionality."""
        self.log("🧪 Testing Security Features", "TEST")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        try:
            import security_utils
            
            # Test security key generation
            test_doc_path = "README.md"  # Use existing file for testing
            if os.path.exists(test_doc_path):
                key = security_utils.generate_document_key(test_doc_path)
                if key and len(key) > 10:
                    self.log("✅ Document key generation works")
                    results["passed"] += 1
                    results["details"].append("✅ Document key generation")
                else:
                    self.log("❌ Document key generation failed", "ERROR")
                    results["failed"] += 1
                    results["details"].append("❌ Document key generation failed")
            
            # Test document hash generation
            if os.path.exists(test_doc_path):
                doc_hash = security_utils.generate_document_hash(test_doc_path)
                if doc_hash and len(doc_hash) > 10:
                    self.log("✅ Document hash generation works")
                    results["passed"] += 1
                    results["details"].append("✅ Document hash generation")
                else:
                    self.log("❌ Document hash generation failed", "ERROR")
                    results["failed"] += 1
                    results["details"].append("❌ Document hash generation failed")
            
            # Test security parameter validation
            security_status = security_utils.validate_security_parameters()
            if isinstance(security_status, dict):
                self.log("✅ Security validation works")
                results["passed"] += 1
                results["details"].append("✅ Security validation")
            else:
                self.log("❌ Security validation failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ Security validation failed")
                
        except Exception as e:
            self.log(f"❌ Security test error: {e}", "ERROR")
            results["failed"] += 1
            results["details"].append(f"❌ Security error: {e}")
        
        self.test_results["security"] = results
        return results["failed"] == 0
    
    def test_qr_functionality(self):
        """Test QR code generation and processing."""
        self.log("🧪 Testing QR Functionality", "TEST")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        try:
            import qr_utils
            
            # Test QR analysis
            test_text = "Hello World Test"
            encoding = qr_utils.analyze_text_encoding(test_text)
            if encoding in ['numeric', 'alphanumeric', 'byte']:
                self.log("✅ QR text encoding analysis works")
                results["passed"] += 1
                results["details"].append("✅ QR text encoding analysis")
            else:
                self.log("❌ QR text encoding analysis failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ QR text encoding analysis failed")
            
            # Test QR capacity calculation
            capacity = qr_utils.calculate_qr_capacity(5, 'M', 'byte')
            if isinstance(capacity, int) and capacity > 0:
                self.log("✅ QR capacity calculation works")
                results["passed"] += 1
                results["details"].append("✅ QR capacity calculation")
            else:
                self.log("❌ QR capacity calculation failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ QR capacity calculation failed")
            
            # Test optimal version calculation
            optimal_version = qr_utils.get_optimal_qr_version(len(test_text), encoding)
            if isinstance(optimal_version, int) and 1 <= optimal_version <= 40:
                self.log("✅ QR optimal version calculation works")
                results["passed"] += 1
                results["details"].append("✅ QR optimal version")
            else:
                self.log("❌ QR optimal version calculation failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ QR optimal version failed")
                
        except Exception as e:
            self.log(f"❌ QR test error: {e}", "ERROR")
            results["failed"] += 1
            results["details"].append(f"❌ QR error: {e}")
        
        self.test_results["qr_functionality"] = results
        return results["failed"] == 0
    
    def test_image_processing(self):
        """Test LSB steganography functionality."""
        self.log("🧪 Testing Image Processing", "TEST")
        
        results = {"passed": 0, "failed": 0, "details": []}
        
        try:
            import lsb_steganography
            
            # Test basic binary conversion functions
            test_int = 123
            binary = lsb_steganography._int_to_binary(test_int, 8)
            converted_back = lsb_steganography._binary_to_int(binary)
            
            if converted_back == test_int:
                self.log("✅ Binary conversion functions work")
                results["passed"] += 1
                results["details"].append("✅ Binary conversion")
            else:
                self.log("❌ Binary conversion functions failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ Binary conversion failed")
            
            # Test LSB bit manipulation
            test_pixel = 127
            test_bit = '1'
            modified_pixel = lsb_steganography._embed_bit(test_pixel, test_bit)
            extracted_bit = lsb_steganography._extract_lsb(modified_pixel)
            
            if extracted_bit == test_bit:
                self.log("✅ LSB bit manipulation works")
                results["passed"] += 1
                results["details"].append("✅ LSB bit manipulation")
            else:
                self.log("❌ LSB bit manipulation failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ LSB bit manipulation failed")
            
            # Test QR validation function
            validation_result = lsb_steganography.validate_qr_for_image(100, 100, 800, 600)
            if isinstance(validation_result, dict) and 'recommendation' in validation_result:
                self.log("✅ QR validation works")
                results["passed"] += 1
                results["details"].append("✅ QR validation")
            else:
                self.log("❌ QR validation failed", "ERROR")
                results["failed"] += 1
                results["details"].append("❌ QR validation failed")
                
        except Exception as e:
            self.log(f"❌ Image processing test error: {e}", "ERROR")
            results["failed"] += 1
            results["details"].append(f"❌ Image processing error: {e}")
        
        self.test_results["image_processing"] = results
        return results["failed"] == 0
    
    def run_all_tests(self):
        """Run all test suites."""
        self.log("🚀 Starting Comprehensive Test Suite", "START")
        start_time = time.time()
        
        test_methods = [
            ("File Structure", self.test_file_structure),
            ("Module Imports", self.test_import_functionality),
            ("QR Functionality", self.test_qr_functionality),
            ("Image Processing", self.test_image_processing),
            ("Security Features", self.test_security_features),
            ("API Endpoints", self.test_api_endpoints),
        ]
        
        passed_suites = 0
        total_suites = len(test_methods)
        
        for suite_name, test_method in test_methods:
            self.log(f"Running {suite_name} tests...", "SUITE")
            try:
                if test_method():
                    passed_suites += 1
                    self.log(f"✅ {suite_name} suite PASSED", "PASS")
                else:
                    self.log(f"❌ {suite_name} suite FAILED", "FAIL")
                    self.failed_tests.append(suite_name)
            except Exception as e:
                self.log(f"❌ {suite_name} suite ERROR: {e}", "ERROR")
                self.failed_tests.append(suite_name)
        
        # Generate summary
        end_time = time.time()
        duration = end_time - start_time
        
        self.log("", "")
        self.log("=" * 60, "")
        self.log("📊 TEST SUMMARY", "SUMMARY")
        self.log("=" * 60, "")
        self.log(f"Total Test Suites: {total_suites}")
        self.log(f"Passed: {passed_suites}")
        self.log(f"Failed: {total_suites - passed_suites}")
        self.log(f"Duration: {duration:.2f} seconds")
        
        if self.failed_tests:
            self.log("", "")
            self.log("❌ Failed Test Suites:", "FAIL")
            for failed_test in self.failed_tests:
                self.log(f"  - {failed_test}", "FAIL")
        else:
            self.log("🎉 All tests passed!", "SUCCESS")
        
        return len(self.failed_tests) == 0
    
    def generate_test_report(self, output_file="test_report.json"):
        """Generate a detailed test report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_suites": len(self.test_results),
                "passed_suites": len(self.test_results) - len(self.failed_tests),
                "failed_suites": len(self.failed_tests),
                "failed_suite_names": self.failed_tests
            },
            "detailed_results": self.test_results
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log(f"📄 Test report saved to: {output_file}")


def main():
    """Main test execution function."""
    parser = argparse.ArgumentParser(description="Steno Application Test Suite")
    parser.add_argument("--test-type", choices=["all", "api", "structure", "security", "qr", "images"], 
                       default="all", help="Type of tests to run")
    parser.add_argument("--base-url", default="http://localhost:5001", 
                       help="Base URL for API testing")
    parser.add_argument("--report", action="store_true", 
                       help="Generate detailed test report")
    
    args = parser.parse_args()
    
    # Initialize test suite
    test_suite = StenoTestSuite(args.base_url)
    
    # Run specific tests based on type
    success = True
    
    if args.test_type == "all":
        success = test_suite.run_all_tests()
    elif args.test_type == "structure":
        success = test_suite.test_file_structure() and test_suite.test_import_functionality()
    elif args.test_type == "api":
        success = test_suite.test_api_endpoints()
    elif args.test_type == "security":
        success = test_suite.test_security_features()
    elif args.test_type == "qr":
        success = test_suite.test_qr_functionality()
    elif args.test_type == "images":
        success = test_suite.test_image_processing()
    
    # Generate report if requested
    if args.report:
        test_suite.generate_test_report()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 
