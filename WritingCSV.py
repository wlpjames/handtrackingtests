import cv2
import numpy as np
import os
import csv
import json

#a function that can do this in a whole video
def format_img(stream, movs={ 'D':[0.0, 0.0], 'O':[0.0, 0.0], 'R':[0.0, 0.0] }):
    
    '''
    
        a template function for how I will get the hand data from a video

        stream : the cv2 stream

        movs : details of the movements
    
    '''
    
    length = int(stream.get(cv2.CAP_PROP_FRAME_COUNT))

    
    if length == 0:
        print('no length : moves = {}'.format(moves))
        return None


    #take movement data
    dist_inc = ( float(movs['D'][1]) - float(movs['D'][0]) ) / length
    rot_inc = ( float(movs['R'][1]) - float(movs['R'][0]) ) / length
    open_inc = ( float(movs['O'][1]) - float(movs['O'][0]) ) / length
        #-------------
    dist = float(movs['D'][0])
    rotation = float(movs['R'][0])
    op = float(movs['O'][0])
    
    print (movs)
    print('stating values at : {}, {}, {}'.format(dist, op, rotation))
    print('length of : {}'.format(length))
    print('increments of : {}, {}, {}'.format(dist_inc, open_inc, rot_inc))
    print()

    #print('num frames : {}, increment size : {}'.format(length, [dist_inc, rot_inc, open_inc]))
    

    #go through, adding all the frames
    data = []
    labels = []
    
    while(True):
        
        ret, frame = stream.read()
        
        if not ret: 
            break
        
        frame = cv2.resize(frame,(256 , 256))
        
        dist += dist_inc
        op += open_inc
        rotation += rot_inc
        
        data.append(np.asarray(frame.data))
        labels.append([dist, op, rotation])
        
    return (np.asarray(data), labels)

def get_mov_values(text):
    
    #example input: "D-0.0-0.0_O-0.0-0.0_R-0.0-0.0"
    #example ouput: movs={ 'D':[0.0, 0.0], 'O':[0.0, 0.0], 'R':[0.0, 0.0] }
    
    #split by underscore
    output = []
    for x in text.split('_'):
        output += [x.split('-')]

    return {'D':output[0][1:], 'O':output[1][1:], 'R':output[2][1:] }


def write_folder(output_file, inpt_folder):
    
    #open file for writing
    with open(output_file, mode='w') as csv_file:
        print('file opened')
        csv_out = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        
        #for each file in the folder
        for file in os.listdir(inpt_folder):

            #translate movement values (coded in image title)
            movements = get_mov_values(file.replace('.mp4', ''))

            returned = format_img(cv2.VideoCapture(inpt_folder + file), movements)

            if returned:
                images, labels = returned 

                for i in range(0, len(images)):

                    #format labels, shape, flat image
                    #csv_out.writerow([movements, labels[i], images[i].shape].append([x for x in images[i].flatten() ]))
                    csv_out.writerow([y for x in movements.values() for y in x] 
                                    + labels[i] 
                                    + [x for x in images[i].shape]
                                    + [x for x in images[i].flatten()])
                    #csv_out.writerow(json.dumps({'movements' : movements, 'labels' : labels[i], 'shape' : images[i].shape, 'image' : images[i].tolist() }))

def format_from_csv(data_as_string):
    data = data_as_string.split(',')
    moves = [float(x) for x in data[:6]]
    labels = [float(x) for x in data[6:9]]
    shape = [int(x) for x in data[9:12]]

    #print(moves, labels, shape)

    image = np.asarray([float(x) for x in data[12:]]).reshape(shape)
    return (moves, labels, shape, image)

def get_num_images():
    with open(csv_path, mode='r') as csv_file:
        line = csv_file.readline()
        cnt = 0
        while line:
            cnt += 1
            line = csv_file.readline()

    return cnt

def get_file_names():
    
    file = os.listdir(inpt_folder)
    file2 = os.listdir(inpt_folder)

    for i in range( len(file) ):
        if file[i] != file2[i]:
            return 'this wont work'

    return file


def loadImage(csv_path):
    #a genorator that gives an image by line by line from the csv
    while True:
        with open(csv_path, mode='r') as csv_file:

            line = csv_file.readline()
            cnt = 1
            while line:

                yield(format_from_csv(line))

                #print("Line {}: {}".format(cnt, line.strip()))
                line = csv_file.readline()
                cnt += 1


if __name__ == "__main__":
    write_folder('images_all_csv.txt', 'test_img/hand_movies/Unprocessed_Clips/')

