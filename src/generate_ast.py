import sys
from io import TextIOWrapper


def define_visitor(
    file: TextIOWrapper, base_class: str, expression_mapping: dict[str, str]
):
    file.write("class Visitor(ABC):\n")

    for expression_type, fields in expression_mapping.items():
        file.write("\t@abstractmethod\n")
        file.write(
            f'\tdef visit_{expression_type.lower()}(self, {expression_type.lower()}: "{expression_type}") -> Any:\n'
        )
        file.write("\t\tpass\n\n")


def define_ast(output_path: str, base_class: str, expression_mapping: dict[str, str]):
    with open(output_path, "w") as file:
        # Write imports
        file.write("from typing import Any\n")
        file.write("from abc import ABC, abstractmethod\n")
        file.write("from dataclasses import dataclass\n\n")
        file.write("from .token import Token\n\n\n")

        # definie the visitor
        define_visitor(file, base_class, expression_mapping)

        # define the Expression base class
        file.writelines(["\n", "\n"])
        file.write(f"class {base_class}(ABC):\n")
        file.write("\t@abstractmethod\n")
        file.write('\tdef accept(self, visitor: "Visitor"):\n')
        file.write("\t\tpass\n\n\n")

        # define the Classes that inherit from base class
        for expression_type, fields in expression_mapping.items():
            field_list = fields.split(",")
            print("Field list: ", field_list)

            file.write("@dataclass\n")
            field_str = ""
            for field in field_list:
                field_str += f"\t{field.strip()}\n"

            file.write(f"class {expression_type}({base_class}):\n")
            file.write(f"{field_str}\n")

            # define the accept method on each type
            file.write("\tdef accept(self, visitor: Visitor):\n")
            file.write(
                f"\t\treturn visitor.visit_{expression_type.lower()}(self)\n\n\n"
            )


def append_to_ast(output_path: str, base_class: str, statement_mapping: dict[str, str]):
    with open(output_path, "a+") as file:
        # define the Statement base class
        file.writelines(["\n", "\n"])
        file.write(f"class {base_class}(ABC):\n")
        file.write("\t@abstractmethod\n")
        file.write('\tdef accept(self, visitor: "Visitor"):\n')
        file.write("\t\tpass\n\n\n")

        # define the Classes that inherit from base class
        for statement_type, fields in statement_mapping.items():
            field_list = fields.split(",")
            print("Field list: ", field_list)

            file.write("@dataclass\n")
            field_str = ""
            for field in field_list:
                field_str += f"\t{field.strip()}\n"

            file.write(f"class {statement_type}({base_class}):\n")
            file.write(f"{field_str}\n")

            # define the accept method on each type
            file.write("\tdef accept(self, visitor: Visitor):\n")
            file.write(f"\t\treturn visitor.visit_{statement_type.lower()}(self)\n\n")


def main():
    if len(sys.argv) != 2:
        print("Usage: generate_ast.py <output_directory>")
        exit(64)

    output_dir = sys.argv[1]
    define_ast(
        output_dir,
        "Expression",
        {
            "Literal": "value: Any",
            "Grouping": "expression: Expression",
            "Unary": "operator: Token, right: Expression",
            "Binary": "left: Expression, operator: Token, right: Expression",
        },
    )

    append_to_ast(
        output_dir,
        "Statement",
        {
            "Expr": "expression: Expression",
            "Print": "expression: Expression",
        },
    )


if __name__ == "__main__":
    main()
