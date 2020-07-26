def compute_alignment(symbols, offsets, lengths, duration):
    total_length = offsets[-1] + lengths[-1]
    epoch = duration / float(total_length)

    print("Epoch = " + str(epoch), "Total length: " + str(total_length))

    alignment = list()
    for idx in range(len(symbols)):
        symbol = symbols[idx]
        offset = offsets[idx]
        if symbol != "<eps>":
            alignment.append((symbol, offset * epoch))
    return alignment
