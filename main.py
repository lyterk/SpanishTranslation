import asyncio
import sys
from src.spanishdict import process_file


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    asyncio.run(process_file(input_file, output_file))
