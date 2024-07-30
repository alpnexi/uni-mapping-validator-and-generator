# UNI Mapping Generator

This project automates the generation of message mapper classes, updates the message type indicator mapping and adds the desired field mapper into the message mapper. It can read input from an Excel file and generate or modify Java classes based on the provided parameters.

## Prerequisites

- Python 3.x
- pandas
- jinja2
- termcolor
- An Excel file with the necessary data and format 

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/mapper-class-generator.git
    cd mapper-class-generator
    ```

2. Install the required Python packages:
    ```sh
    pip install pandas jinja2 termcolor
    ```

## Usage

1. Ensure your Excel file is named `Mapping_PSP to ISO20022_MTI12XX_V2.0.xlsx` and is located in the same directory as the script.
   If one doesn't want to supply an Excel file, can change the main method to instead supply the necessary message funtion, direction, etc. 

2. Run the script:
    ```sh
    python generate_setup.py
    python add_mapper_UMM2ISO.py
    ```

3. Follow the prompts or change the main method to enter the necessary information:
    - Message function description
    - Directions needed (e.g., 1,3)


### `main()`
The main function that executes the generation process.

## License

This project is licensed under the ??? License - see the [LICENSE](LICENSE) file for details.