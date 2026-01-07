from core.logic import add, determine_path


def main() -> None:
    
    result = add(3, 4)
    print("Result:", result)

    print("Plan:", determine_path("Beginner"))


if __name__ == "__main__":
    main()
