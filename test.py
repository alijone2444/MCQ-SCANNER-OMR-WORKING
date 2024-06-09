def sort_pixels(pixels, method="left-to-right"):
    # Initialize the reverse flag and sort index
    reverse = False
    i = 0

    # Handle if we need to sort in reverse
    if method == "right-to-left":
        reverse = True

    # Sort the list of pixels based on x first, then y
    sorted_pixels = sorted(pixels, key=lambda p: (p[0], p[1]), reverse=reverse)

    # Sort pixels in groups of three by y-coordinate
    two_d_array = []
    for i in range(0, len(sorted_pixels), 3):
        group = sorted(sorted_pixels[i:i+3], key=lambda p: p[1])
        two_d_array.append(group)

    # Find the maximum length of any sublist
    max_length = max(len(sublist) for sublist in two_d_array)

    # Reshape the list
    reshaped_list = []
    for i in range(max_length):
        reshaped_list.append([sublist[i] if i < len(sublist) else None for sublist in two_d_array])
    
    final_array = [item for sublist in reshaped_list for item in sublist if item is not None]

    return final_array

# Given pixel coordinates
# vec = [(299, 597), (130, 595), (299, 529), (132, 526), (460, 526), (299, 462), (135, 461), (460, 460)]


# vec = [(1,5),(2,5),(1,2),(1,10),(3,5)]

# # Sort pixels left-to-right
# sorted_pixels_lr = sort_pixels(vec)
# print("Sorted pixels (left-to-right):", sorted_pixels_lr)

