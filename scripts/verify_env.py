# -*- coding: utf-8 -*-
"""
verify_env.py
Verifies the system environment specifications, Python runtime, PyTorch capability, 
CUDA hardware acceleration availability, and VRAM properties.
"""

import sys
import platform
import os
from typing import Dict, Any

def get_cpu_info() -> str:
    """Retrieve basic CPU information in a platform-independent way."""
    try:
        return f"{platform.processor()} ({platform.machine()})"
    except Exception:
        return "Unknown CPU"

def verify_system_specs() -> Dict[str, Any]:
    """Inspect and collect hardware and software platform characteristics."""
    specs: Dict[str, Any] = {}
    
    # Python Version
    python_ver = sys.version_info
    specs["python_version"] = f"{python_ver.major}.{python_ver.minor}.{python_ver.micro}"
    specs["python_ok"] = (python_ver.major == 3 and python_ver.minor >= 10)
    
    # OS Info
    specs["os"] = f"{platform.system()} {platform.release()}"
    specs["cpu"] = get_cpu_info()
    
    # PyTorch and CUDA info
    try:
        import torch
        specs["torch_installed"] = True
        specs["torch_version"] = torch.__version__
        specs["cuda_available"] = torch.cuda.is_available()
        
        if specs["cuda_available"]:
            specs["cuda_device_count"] = torch.cuda.device_count()
            specs["cuda_device_name"] = torch.cuda.get_device_name(0)
            # VRAM
            total_vram_bytes = torch.cuda.get_device_properties(0).total_memory
            specs["total_vram_gb"] = round(total_vram_bytes / (1024 ** 3), 2)
        else:
            specs["cuda_device_count"] = 0
            specs["cuda_device_name"] = "N/A"
            specs["total_vram_gb"] = 0.0
            
    except ImportError:
        specs["torch_installed"] = False
        specs["torch_version"] = "Not Installed"
        specs["cuda_available"] = False
        specs["cuda_device_count"] = 0
        specs["cuda_device_name"] = "N/A"
        specs["total_vram_gb"] = 0.0

    # Dependencies check
    packages = ["transformers", "pandas", "langchain", "huggingface_hub", "sklearn"]
    package_status: Dict[str, str] = {}
    for pkg in packages:
        try:
            if pkg == "sklearn":
                import sklearn
                package_status[pkg] = sklearn.__version__
            else:
                imported = __import__(pkg)
                package_status[pkg] = getattr(imported, "__version__", "Installed")
        except ImportError:
            package_status[pkg] = "Missing"
    
    specs["packages"] = package_status
    return specs

def print_report(specs: Dict[str, Any]) -> None:
    """Output formatted environment validation report to stdout."""
    print("=" * 60)
    print("ENVIRONMENT VALIDATION REPORT — PHASE 0")
    print("=" * 60)
    
    # Python Version
    status = "OK" if specs["python_ok"] else "FAILED (Requires >= 3.10)"
    print(f"Python Version : {specs['python_version']} [{status}]")
    print(f"Platform OS    : {specs['os']}")
    print(f"CPU Info       : {specs['cpu']}")
    
    # PyTorch & CUDA
    print("-" * 60)
    print("GPU & ACCELERATION SPECIFICATIONS")
    print("-" * 60)
    print(f"PyTorch Version: {specs['torch_version']}")
    cuda_status = "Available" if specs["cuda_available"] else "Not Available"
    print(f"CUDA status    : {cuda_status}")
    if specs["cuda_available"]:
        print(f"CUDA Devices   : {specs['cuda_device_count']}")
        print(f"Primary GPU    : {specs['cuda_device_name']}")
        print(f"Total VRAM     : {specs['total_vram_gb']} GB")
    else:
        print("WARNING: CUDA acceleration is not active. Local runs will use CPU.")

    # Library Status
    print("-" * 60)
    print("DEPENDENCY PACKAGE STATUS")
    print("-" * 60)
    for pkg, ver in specs["packages"].items():
        print(f" - {pkg:<20}: {ver}")
    print("=" * 60)

def main() -> None:
    specs = verify_system_specs()
    print_report(specs)
    
    # Exit with code 0 if Python is valid, otherwise 1
    if not specs["python_ok"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
