import numpy as np
import gmpy2
from gmpy2 import mpz, mpfr


'''
Dictionaries for mapping letters to indices and vice-versa
'''

init_str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ. ?'
i = 0
dict = {}
for letter in init_str:
    dict[letter] = i
    i += 1
rev_dict = {}
for j in range(len(init_str)):
    rev_dict[j] = init_str[j]

'''
User class for object oriented interaction
'''

class User:
    def __init__(self, name, gen, priv, p):
        self.name = name
        self.gen = gen
        self.priv = priv
        self.p = p
        self.block_size = int(gmpy2.rint_floor(gmpy2.div(gmpy2.log(p), gmpy2.log(29))))
        self.public_number = gmpy2.powmod(self.gen, self.priv, self.p)
    
    def gen_priv_number(self, public_number_b):
        self.private_number = gmpy2.powmod(public_number_b, self.priv, self.p)
        
    def gen_keys(self):
        if gmpy2.is_odd(self.private_number):
            self.csk = self.private_number
        else:
            self.csk = gmpy2.sub(self.private_number, 1)
        self.dk = gmpy2.invert(self.csk, gmpy2.sub(self.p, 1))
    
    def convert_pl_block(self, word):
        exp = 0
        pl_number = 0
        for i in range(len(word)-1, -1, -1):
            pl_number += dict[word[i]]*(29**exp)
            exp += 1

        et_number = gmpy2.powmod(pl_number, self.csk, self.p)

        et_block = ""

        for i in range(self.block_size+1):
            et_number, curr_ind = gmpy2.f_divmod(et_number, 29)
            et_block = rev_dict[curr_ind]+et_block

        return et_block
    
    def convert_et_block(self, word):
        exp = 0
        et_number = 0
        for i in range(len(word)-1, -1, -1):
            et_number += dict[word[i]]*(29**exp)
            exp += 1

        pl_number = gmpy2.powmod(et_number, self.dk, self.p)

        pl_block = ""

        for i in range(self.block_size):
            pl_number, curr_ind = gmpy2.f_divmod(pl_number, 29)
            pl_block = rev_dict[curr_ind]+pl_block

        return pl_block
    
    def receive_message(self, et_list):
        pl_list = [self.convert_et_block(ets) for ets in et_list]
        output = "".join(pl_list)
        output = output.rstrip()
        print(">> User {} received message: {}".format(self.name, output))
    
    def send_number(self, user_b):
        user_b.gen_priv_number(self.public_number)
        user_b.gen_keys()
    
    def send_message(self, user_b, msg_plaintext):
        if not len(msg_plaintext)%self.block_size == 0:
            msg_plaintext += ' '*(self.block_size-(len(msg_plaintext)%self.block_size))
        input_list = [msg_plaintext[i:i+self.block_size] for i in range(0, len(msg_plaintext), self.block_size)]
        et_list = [self.convert_pl_block(pls) for pls in input_list]
        encrypted = "".join(et_list)
        print(">> Sending message from {} to {}: {}".format(self.name, user_b.name, encrypted))
        user_b.receive_message(et_list)


'''
Main(driver) function
'''

if __name__ == "__main__":
    while True:
        p = int(input("Enter an odd prime p such that p = 2*r + 1 and r is prime: "))
        if not gmpy2.is_odd(p) or not gmpy2.is_prime(p):
            print("ERROR! Please enter an odd prime number")
        elif not gmpy2.is_prime(gmpy2.divexact(gmpy2.sub(p, 1), 2)):
            print("ERROR! Please enter an odd prime p SUCH THAT p = 2*r + 1 and r is prime")
        else:
            break
        
    p_set = set(range(1, p))

    while True:
        g = int(input("Enter a generator g for the group Z_p: "))
        flag = False
        g_set = set()
        for x in p_set:
            g_set.add(gmpy2.powmod(g, x, p))
        if not g_set == p_set:
            print("ERROR! Please enter a valid generator for the group Z_p")
        else:
            break

    k1 = gmpy2.mpz_random(gmpy2.random_state(1), p)
    k2 = gmpy2.mpz_random(gmpy2.random_state(2), p)

    Alex = User('Alex', g, k1, p)
    Bob = User('Bob', g, k2, p)
    users = {
        'A' : [Alex, Bob],
        'B' : [Bob, Alex]
    }
    print(">> Generated public number for Alex: ", Alex.public_number)
    print(">> Generated public number for Bob: ", Bob.public_number)
    print("--------------------------------------------------------------------------------------")
    print(">> Sending Alex's public number to Bob")
    Alex.send_number(Bob)
    print(">> Sending Bob's public number to Alex")
    Bob.send_number(Alex)
    print("--------------------------------------------------------------------------------------")
    print(">> Generated common session key for both users")
    while True:
        print("--------------------------------------------------------------------------------------")
        user_str = input(">> Please select sender (A for Alex, B for Bob): ")
        if not user_str:
            break
        if user_str not in users.keys():
            print("ERROR! Please type A for Alex and B for Bob")
            continue
        else:
            user = users[user_str]
        msg = input(">> Please type a message for {} to send to {}: ".format(user[0].name, user[1].name)).upper()
        flag = False
        for letters in msg:
            if letters not in dict.keys():
                flag = True
                break
        if flag:
            print("ERROR! Message must only contain letters: ['a'-'z'], ['A'-'Z'], '.', ' ', '?'")
            continue
        if not msg:
            break
        user[0].send_message(user[1], msg)