import random, os
from hangman_art import stages, logo 
from hangman_words import word_list

display = []
chosen_word = random.choice(word_list)
lives = 6
already_guess = []
print(f'Suỵt, đáp án là: {chosen_word}.')

for _ in range(len(chosen_word)):
    display.append("_")

end_of_game = False
print(logo)

while not end_of_game:
    guess = input("Nhập chữ cái bạn đoán:\n").lower()
    os.system('cls')
    for position in range(len(chosen_word)):
        if guess == chosen_word[position]:
            display[position] = guess
    if guess in already_guess:
        print(f"Bạn đã đoán chữ {guess} rồi.")
    elif guess not in chosen_word:
        print(f"Bạn đoán chữ {guess} nhưng sai mất rồi. Bạn mất 1 mạng.")
        lives -= 1
    already_guess.append(guess)
    print(f"{' '.join(display)}")
    print(stages[lives])
    if "_" not in display:
        end_of_game = True
        print("Bạn thắng!")   
    elif lives == 0:
        end_of_game = True
        print("Bạn thua!")
