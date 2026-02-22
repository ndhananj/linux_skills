# Infrastructure as Code and CI/CD

This skill covers provisioning and managing cloud infrastructure using Terraform, automating configuration management with Ansible, and integrating these tools into CI/CD pipelines.

## Concepts

**Infrastructure as Code (IaC)** treats infrastructure configuration as software: it is version-controlled, peer-reviewed, and automatically applied. This eliminates configuration drift and makes environments reproducible.

**Terraform** is a declarative IaC tool by HashiCorp. You describe the desired state of your infrastructure in HCL (HashiCorp Configuration Language) files, and Terraform determines the sequence of API calls needed to reach that state. The **state file** (`terraform.tfstate`) records the current known state of all managed resources.

**Ansible** is an agentless configuration management and orchestration tool. It connects to hosts over SSH and executes **playbooks** — YAML files that describe the desired state of those hosts. Ansible is idempotent: running the same playbook multiple times produces the same result.

## Tools Available

| Tool | Description |
|------|-------------|
| `terraform_init` | Initialise a Terraform working directory |
| `terraform_plan` | Preview changes before applying |
| `terraform_apply` | Apply the planned changes |
| `terraform_destroy` | Destroy all managed resources |
| `terraform_output` | Show output values from the state |
| `terraform_validate` | Validate configuration syntax |
| `terraform_fmt` | Format configuration files |
| `terraform_state_list` | List resources in the state file |
| `terraform_import` | Import an existing resource into state |
| `ansible_ping` | Test connectivity to managed hosts |
| `ansible_run_module` | Run an ad-hoc Ansible module |
| `ansible_playbook` | Execute an Ansible playbook |

## Usage Examples

**Initialise and preview a Terraform deployment:**
```
terraform_init(working_dir="/opt/infra")
terraform_plan(working_dir="/opt/infra", out_file="plan.out")
```

**Apply changes automatically:**
```
terraform_apply(working_dir="/opt/infra", plan_file="plan.out", auto_approve=True)
```

**Run an Ansible playbook in check mode:**
```
ansible_playbook(playbook="site.yml", inventory="inventory/prod", check=True)
```

## Skill Levels

**Entry** — Understand what IaC is and why it matters; run `terraform plan` and `apply` against a simple configuration.

**Beginner** — Write basic Terraform resources (VMs, networks, storage); write simple Ansible playbooks to install packages and manage files.

**Intermediate** — Use Terraform modules and remote state; write Ansible roles; integrate both tools into a CI/CD pipeline (GitHub Actions, GitLab CI).

**Advanced** — Design multi-environment Terraform architectures with workspaces; implement Ansible dynamic inventories; manage secrets with Vault.
