def all_answer_equal(answers):
    data = [x.content for x in answers]
    return data[1:] == data[:-1]
