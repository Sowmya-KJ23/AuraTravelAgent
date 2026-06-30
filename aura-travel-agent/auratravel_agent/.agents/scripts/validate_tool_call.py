import sys
import json

def main():
    try:
        # Read the JSON payload from stdin
        payload = json.load(sys.stdin)
        tool_call = payload.get("toolCall", {})
        tool_args = tool_call.get("args", {})
        command = tool_args.get("CommandLine", "").strip()

        # Block destructive commands like "rm -rf /"
        normalized_command = " ".join(command.split())  # normalize whitespace
        if "rm -rf /" in normalized_command or ("rm" in normalized_command and "-rf" in normalized_command and "/" in normalized_command):
            decision = {
                "decision": "deny",
                "reason": f"Execution blocked: Command '{command}' is destructive and not allowed."
            }
            print(json.dumps(decision))
            sys.exit(2)

        # Allow other commands
        print(json.dumps({"decision": "allow"}))
        sys.exit(0)

    except Exception as e:
        # Fallback to deny on failure for safety
        print(json.dumps({"decision": "deny", "reason": f"Hook validation failed: {str(e)}"}))
        sys.exit(2)

if __name__ == "__main__":
    main()
