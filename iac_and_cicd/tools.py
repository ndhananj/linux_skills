"""
iac_and_cicd/tools.py — Tools for Infrastructure as Code (Terraform, Ansible) and CI/CD pipelines.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "runtime"))
from command_runner import run_command


# ---------------------------------------------------------------------------
# Terraform
# ---------------------------------------------------------------------------

def terraform_init(working_dir: str = ".") -> str:
    """Initialise a Terraform working directory.

    working_dir: Path to the directory containing Terraform configuration files.
    """
    return run_command(["terraform", "init"], cwd=working_dir)


def terraform_plan(working_dir: str = ".", out_file: str = None) -> str:
    """Generate and show a Terraform execution plan.

    working_dir: Path to the Terraform configuration directory.
    out_file: Optional path to save the plan to a file.
    """
    cmd = ["terraform", "plan"]
    if out_file:
        cmd.extend(["-out", out_file])
    return run_command(cmd, cwd=working_dir)


def terraform_apply(working_dir: str = ".", plan_file: str = None, auto_approve: bool = False) -> str:
    """Apply a Terraform execution plan.

    working_dir: Path to the Terraform configuration directory.
    plan_file: Optional path to a saved plan file.
    auto_approve: When True, skip interactive approval.
    """
    cmd = ["terraform", "apply"]
    if auto_approve:
        cmd.append("-auto-approve")
    if plan_file:
        cmd.append(plan_file)
    return run_command(cmd, cwd=working_dir)


def terraform_destroy(working_dir: str = ".", auto_approve: bool = False) -> str:
    """Destroy Terraform-managed infrastructure.

    working_dir: Path to the Terraform configuration directory.
    auto_approve: When True, skip interactive approval.
    """
    cmd = ["terraform", "destroy"]
    if auto_approve:
        cmd.append("-auto-approve")
    return run_command(cmd, cwd=working_dir)


def terraform_output(working_dir: str = ".", output_name: str = None) -> str:
    """Show Terraform output values.

    working_dir: Path to the Terraform configuration directory.
    output_name: Optional name of a specific output to show.
    """
    cmd = ["terraform", "output", "-json"]
    if output_name:
        cmd.append(output_name)
    return run_command(cmd, cwd=working_dir)


def terraform_validate(working_dir: str = ".") -> str:
    """Validate Terraform configuration files.

    working_dir: Path to the Terraform configuration directory.
    """
    return run_command(["terraform", "validate"], cwd=working_dir)


def terraform_fmt(working_dir: str = ".", check_only: bool = False) -> str:
    """Format Terraform configuration files.

    working_dir: Path to the Terraform configuration directory.
    check_only: When True, check formatting without making changes.
    """
    cmd = ["terraform", "fmt", "-recursive"]
    if check_only:
        cmd.append("-check")
    return run_command(cmd, cwd=working_dir)


def terraform_state_list(working_dir: str = ".") -> str:
    """List resources in the Terraform state.

    working_dir: Path to the Terraform configuration directory.
    """
    return run_command(["terraform", "state", "list"], cwd=working_dir)


def terraform_import(resource_address: str, resource_id: str, working_dir: str = ".") -> str:
    """Import an existing resource into Terraform state.

    resource_address: Terraform resource address, e.g. 'aws_instance.web'.
    resource_id: Cloud provider resource ID to import.
    working_dir: Path to the Terraform configuration directory.
    """
    return run_command(["terraform", "import", resource_address, resource_id], cwd=working_dir)


# ---------------------------------------------------------------------------
# Ansible
# ---------------------------------------------------------------------------

def ansible_ping(inventory: str, hosts: str = "all") -> str:
    """Test connectivity to Ansible-managed hosts.

    inventory: Path to the Ansible inventory file.
    hosts: Host pattern to target, e.g. 'all' or 'webservers'.
    """
    return run_command(["ansible", "-i", inventory, hosts, "-m", "ping"])


def ansible_run_module(inventory: str, hosts: str, module: str, args: str = None) -> str:
    """Run an Ansible module on managed hosts.

    inventory: Path to the Ansible inventory file.
    hosts: Host pattern to target.
    module: Ansible module name, e.g. 'shell', 'copy', 'apt'.
    args: Module arguments as a string, e.g. 'name=nginx state=present'.
    """
    cmd = ["ansible", "-i", inventory, hosts, "-m", module]
    if args:
        cmd.extend(["-a", args])
    return run_command(cmd)


def ansible_playbook(playbook: str, inventory: str, extra_vars: str = None, check: bool = False) -> str:
    """Run an Ansible playbook.

    playbook: Path to the playbook YAML file.
    inventory: Path to the Ansible inventory file.
    extra_vars: Extra variables as a JSON string or key=value pairs.
    check: When True, run in check mode (dry run) without making changes.
    """
    cmd = ["ansible-playbook", "-i", inventory, playbook]
    if extra_vars:
        cmd.extend(["--extra-vars", extra_vars])
    if check:
        cmd.append("--check")
    return run_command(cmd)
