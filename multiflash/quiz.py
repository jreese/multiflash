# Copyright 2020 John Reese
# Licensed under the MIT License

import textwrap
import click
import random
from typing import List, Set

from multiflash.dataset import Fact, Facts, connect
from multiflash.question import GuessValue, GuessKeyword, Question


class Quiz:
    def __init__(self, class_name: str, num_choices: int = 3):
        self.class_name = class_name
        self.num_choices = num_choices

        self.counter: int = 1
        self.questions: List[Question] = []

        self._facts: Set[Fact] = set()

    @property
    def facts(self) -> Set[Fact]:
        if not self._facts:
            db, engine = connect()
            query = Facts.select().where(Facts.class_name == self.class_name)
            cursor = db.execute(*engine.prepare(query))
            rows = cursor.fetchall()
            self._facts.update(Fact(**row) for row in rows)
        return self._facts

    def generate(self) -> List[Question]:
        questions: List[Question] = []

        all_facts = self.facts
        num_incorrect = self.num_choices - 1

        for guess_type in (GuessKeyword, GuessValue):
            for fact in all_facts:
                incorrect = random.sample(all_facts - {fact}, num_incorrect)
                q = guess_type(fact, incorrect)
                questions.append(q)

        return questions

    def ask(self, question: Question) -> bool:
        click.echo(f"\nQuestion {self.counter}: {question.ask()}\n")

        letter = ord("a")
        choices = question.choices()
        answer = question.answer()

        for choice in random.sample(choices, len(choices)):
            if choice == answer:
                answer = chr(letter)
            click.echo(f"  {chr(letter)}: {choice}")
            letter += 1

        if question.full_answer:
            response = click.prompt("\nAnswer (full keyword): ", prompt_suffix="")
        else:
            response = click.prompt("\nAnswer (letter): ", prompt_suffix="")

        if response.lower() == answer.lower():
            click.echo("Correct!")
            return True

        else:
            click.echo(f"Incorrect. Correct answer was {answer!r}")
            return False

    def start(self):
        questions = self.generate()
        random.shuffle(questions)

        score = 0
        for question in questions:
            correct = self.ask(question)
            if correct:
                score += 1

        click.echo(f"\nQuiz complete. You scored {score} / {len(questions)} correct!")