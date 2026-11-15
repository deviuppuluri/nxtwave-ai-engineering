from app.hardware import collect_hardware_info


def answer_question(question, hardware=None):
    """Answer common hardware questions using collected system data."""
    data = hardware if hardware is not None else collect_hardware_info()
    q = question.lower().strip()

    if not q:
        return "Please enter a question."

    if any(word in q for word in ["cpu", "processor", "core"]):
        result = data.get("cpu", {})
        if result.get("available"):
            return "CPU information:\n" + result.get("output", "")
        return "CPU information is unavailable: " + result.get("error", "Unknown reason")

    if any(word in q for word in ["memory", "ram"]):
        result = data.get("memory_proc", {})
        if result.get("available"):
            info = result.get("data", {})
            total = info.get("MemTotal", "Unknown")
            available = info.get("MemAvailable", "Unknown")
            return f"Memory information:\nTotal RAM: {total}\nAvailable RAM: {available}"
        return "Memory information is unavailable."

    if any(word in q for word in ["disk", "storage", "drive"]):
        result = data.get("storage", {})
        if result.get("available"):
            return "Storage information:\n" + result.get("output", "")
        return "Storage information is unavailable: " + result.get("error", "")

    if any(word in q for word in ["gpu", "graphics", "display"]):
        result = data.get("pci_devices", {})
        if result.get("available"):
            lines = [
                line for line in result.get("output", "").splitlines()
                if any(word in line.lower() for word in ["vga", "3d", "display"])
            ]
            if lines:
                return "Graphics devices:\n" + "\n".join(lines)
            return "No graphics device was identified in the PCI information."
        return "Graphics information is unavailable: " + result.get("error", "")

    if any(word in q for word in ["operating system", "linux version", "system"]):
        os_info = data.get("os", {})
        return (
            f"Operating system: {os_info.get('system', 'Unknown')}\n"
            f"Release: {os_info.get('release', 'Unknown')}\n"
            f"Architecture: {os_info.get('machine', 'Unknown')}"
        )

    if "help" in q:
        return "Ask about CPU, RAM, memory, disk, storage, GPU, graphics, or operating system."

    return (
        "I can answer questions about CPU, RAM, storage, GPU, "
        "and operating system using collected system information."
    )


def main():
    print("Linux Hardware Q&A Assistant")
    print("Ask about CPU, RAM, disk, GPU, or operating system.")
    print("Type 'exit' to quit.\n")

    hardware = collect_hardware_info()

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if question.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        print("\nAssistant:", answer_question(question, hardware), "\n")


if __name__ == "__main__":
    main()
