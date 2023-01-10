import bcrypt


def main() -> bytes:
    return bcrypt.gensalt()


if __name__ == "__main__":
    salt: bytes = main()
    print(salt)