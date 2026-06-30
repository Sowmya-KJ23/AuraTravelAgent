import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.resolve()))

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from auratravel_agent.agent import root_agent


def main():
    dataset_path = Path("tests/eval/datasets/basic-dataset.json")
    output_path = Path("artifacts/traces/basic-traces.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Loading dataset from {dataset_path}...")
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)

    eval_cases = dataset.get("eval_cases", [])

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent, session_service=session_service, app_name="auratravel_agent"
    )

    processed_cases = []

    for i, case in enumerate(eval_cases):
        case_id = case.get("eval_case_id", f"case_{i}")
        prompt_text = case["prompt"]["parts"][0]["text"]
        if i > 0:
            import time

            print("Waiting 20 seconds to respect API rate limits...")
            time.sleep(20)
        print(
            f"Running scenario {i + 1}/{len(eval_cases)}: {case_id} ('{prompt_text[:30]}...')"
        )

        session = session_service.create_session_sync(
            user_id=f"eval_user_{case_id}", app_name="auratravel_agent"
        )

        message = types.Content(
            role="user", parts=[types.Part.from_text(text=prompt_text)]
        )

        # Run the workflow runner locally
        events = list(
            runner.run(
                new_message=message,
                user_id=f"eval_user_{case_id}",
                session_id=session.id,
                run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            )
        )

        # Build the turns and events for the trace
        # First event in trace turns is the user query
        turn_events = [
            {
                "author": "user",
                "content": {"role": "user", "parts": [{"text": prompt_text}]},
            }
        ]

        final_text = ""
        for event in events:
            # Skip user event (it's already added) and serialize other events
            if event.author == "user":
                continue

            event_dict = {
                "author": event.author or "agent",
                "content": {"role": "model", "parts": []},
            }

            if event.content and event.content.parts:
                for part in event.content.parts:
                    part_dict = {}
                    if part.text:
                        part_dict["text"] = part.text
                        if event.author in ("itinerary_generator", "ask_clarification"):
                            final_text += part.text
                    elif part.function_call:
                        part_dict["function_call"] = {
                            "name": part.function_call.name,
                            "args": part.function_call.args,
                        }
                    elif part.function_response:
                        part_dict["function_response"] = {
                            "name": part.function_response.name,
                            "response": part.function_response.response,
                        }

                    if part_dict:
                        event_dict["content"]["parts"].append(part_dict)

            if event_dict["content"]["parts"]:
                turn_events.append(event_dict)

        # Build the final EvalCase JSON structure
        eval_case = {
            "eval_case_id": case_id,
            "prompt": case["prompt"],
            "agent_data": {"turns": [{"turn_index": 0, "events": turn_events}]},
        }

        if final_text:
            eval_case["responses"] = [
                {"response": {"role": "model", "parts": [{"text": final_text}]}}
            ]

        processed_cases.append(eval_case)

    # Save traces to JSON
    output_dataset = {"eval_cases": processed_cases}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_dataset, f, indent=2, ensure_ascii=False)

    print(f"Traces saved successfully to {output_path}")


if __name__ == "__main__":
    main()
