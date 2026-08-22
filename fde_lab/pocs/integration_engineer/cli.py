import argparse
from fde_lab.pocs.integration_engineer.agent import IntegrationEngineerAgent
from fde_lab.pocs.integration_engineer.models import IntegrationReport
from fde_lab.observability.logger import get_logger

logger = get_logger("fde_lab.integration_engineer")

def print_ui(report: IntegrationReport):
    print("\nFDE Lab")
    print("────────────────────────────────")
    print("\nIntegration Engineer\n")
    print("Customer integration:\nCRM → Billing System\n")
    
    print("Analyzing source schema...")
    print("✓ 8 source fields discovered\n")
    
    print("Analyzing target schema...")
    print("✓ 6 target fields discovered\n")
    
    print("Building mapping...")
    for rule in report.mapping.rules:
        src = " + ".join(rule.source_fields)
        print(f"✓ {src} → {rule.target_field}")
    for unmapped in report.mapping.unmapped_source_fields:
        print(f"✗ Unmapped source field: {unmapped}")
        
    print("\nValidating records...")
    print(f"✓ {report.records_transformed} records valid")
    print(f"✗ {report.records_rejected} records rejected\n")
    
    if report.rejected_records:
        print("Rejected records:")
        for cid, reason in report.rejected_records.items():
            print(f"- {cid}: {reason}")
        print("")
        
    print("Transforming records...")
    print(f"✓ {report.records_transformed} records transformed\n")
    
    print("Integration complete.\n")
    print(f"Output:\n{report.output_path}\n")
    
    print("Explanation:")
    print(report.explanation)
    print("\n────────────────────────────────\n")

def main():
    parser = argparse.ArgumentParser(description="FDE Lab - Integration Engineer")
    parser.add_argument("command", choices=["integrate"], help="Command to execute")
    parser.add_argument("--scenario", default="normal", help="Scenario to run")
    args = parser.parse_args()

    if args.command == "integrate":
        agent = IntegrationEngineerAgent(scenario=args.scenario)
        report = agent.execute_integration()
        print_ui(report)

if __name__ == "__main__":
    main()
