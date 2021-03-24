# https://github.com/matcool/anvil-parser
import anvil
# get directory contents
# https://stackoverflow.com/a/3964691
import glob, os
# command line arguments
import getopt, sys
# execution time
import time
# used to handle exceptions properly
# https://stackoverflow.com/a/16946886/3809002
import traceback

# helps with multithreading data-passing, see below stackoverflow reference on multithreading
import itertools

# multithreading
# https://stackoverflow.com/a/28463266/3809002
from multiprocessing.dummy import Pool as ThreadPool


# setup

input_arguments = sys.argv
argument_list = input_arguments[5:] # all but first, which is filename (and three world directories)
print("====================================================================================================")
print("ALL ARGUMENTS: ", input_arguments)
print("ARGUMENTS: ", argument_list)

a_pre = input_arguments[1]
a_post = input_arguments[2]
a_new = input_arguments[3]
a_output = input_arguments[4]
threads = 1
verbose = False
include_bedrock = False
handle_entities = True
wd = os.getcwd()

print("pre:",a_pre,"post:",a_post,"new:",a_new,"output:",a_output)
print("wd:",wd)
print("====================================================================================================")

# https://stackoverflow.com/a/1557584
# windows use time.clock, else use time.time
start_time = time.time()

short_options = "hvbt:e"
long_options = ["help", "verbose", "bedrock", "threads=", "entities"]
try:
	arguments, values = getopt.getopt(argument_list, short_options, long_options)
except getopt.error as err:
	# Output error, and return with an error code
	print (str(err))
	sys.exit(2)

# Evaluate given options
for current_argument, current_value in arguments:
	if current_argument in ("-v", "--verbose"):
		print ("Enabling verbose mode")
		verbose = True
	elif current_argument in ("-h", "--help"):
		print ("Displaying help")
	elif current_argument in ("-b", "--bedrock"):
		print ("ENABLING THE SCANNING OF y=0... checking bedrock layer...")
		include_bedrock = True
	elif current_argument in ("-e", "--entities"):
		print ("Disabling entity migration")
		handle_entities = False
	elif current_argument in ("-t", "--threads"):
		if current_value.isnumeric():
			print (("Thread count set to (%s)") % (current_value))
			threads = int(current_value)
		else:
			print("Attempted to set thread count to ", current_value, "however, input not a valid number")


#
#
#
#
#

def printv(*args: object):
	if verbose:
		print("[v]",*args)

def printp(file, *args: object):
	#print(file)
	split_file = file.split(".")
	region_x = int(split_file[1])
	region_z = int(split_file[2])
	print("REGION[","{:03d}".format(region_x),"{:03d}".format(region_z),"]",*args)

#printp("hey","my message")


wd_pre_region = wd + "\\" + a_pre + "\\region\\"
wd_post_region = wd + "\\" + a_post + "\\region\\"
wd_new_region = wd + "\\" + a_new + "\\region\\"
wd_output_region = wd + "\\" + a_output + "\\region\\"

# create output world directory if does not exist
if not os.path.exists(wd_output_region):
	os.makedirs(wd_output_region)

# python negative.py world3-pre world-active world-output -v
os.chdir(a_post + "/region") # "/mydir"
file_count = 0
chunks_processed = 0
filelist = glob.glob("*.mca")

def process_region(file, wd_pre_region, wd_post_region, wd_new_region, wd_output_region, include_bedrock):
	#file_count += 1
	split_file = file.split(".")
	region_x = int(split_file[1])
	region_z = int(split_file[2])
	#print(region_x,region_z)
	#print("REGION:","r[","{:03d}".format(region_x),"{:03d}".format(region_z),"]",file)
	printp(file,"new thread launched")

	#t_file = wd + "\\" + a_post + "\\region\\" + file

	#test = anvil.Region.from_file(t_file)
	#print("worked")

	if True:

		post_region = anvil.Region.from_file(wd_post_region + file)
		if os.path.isfile(wd_pre_region + file) and os.path.isfile(wd_new_region + file):
			printp(file,"region file exists in all. processing")

			pre_region = anvil.Region.from_file(wd_pre_region + file)

			new_region = anvil.Region.from_file(wd_new_region + file)

			# Create a new region with the `EmptyRegion` class at 0, 0 (in region coords)
			output_region = anvil.EmptyRegion(region_x, region_z)


			# Chunks are 16 blocks wide, 16 blocks long, 256 blocks high, and 65536 blocks total.

			# region has 32*32 chunks, 1024 total.

			# one region contains 1024*65536 blocks total = 67,108,864 blocks

			# http://www.dinnerbone.com/minecraft/tools/coordinates/

			# minecraft region x,z contains blocks from x=x*512,z=z*512 to x=((x+1)*512)-1, z=((z+1)*512)-1

			# r.20.-16.mca
			# contains blocks 10240,0,-8192 to 10751,255,-7681

			#each chunk
			block_count = 0
			chunk_count = 0
			for local_chunk_x in range(32):
				for local_chunk_z in range(32):
					chunk_count += 1
					chunk_diff = False
					entitydataset = False
					printv("--")
					printv(chunk_count,"CHUNK:",local_chunk_x,local_chunk_z)

					# global chunk section cords [x,z]
					glob_chunk_x = (region_x*32)+local_chunk_x
					glob_chunk_z = (region_z*32)+local_chunk_z
					printv("local chunk id :",local_chunk_x,local_chunk_z)
					printv("g chunk section:",glob_chunk_x,glob_chunk_z)

					# checked as accurate against Coordinate Tools http://www.dinnerbone.com/minecraft/tools/coordinates/
					# global chunk block coordinate range. [x,y,z]
					global_chunk_range_x = range(glob_chunk_x*16,glob_chunk_x*16+16)
					global_chunk_range_z = range(glob_chunk_z*16,glob_chunk_z*16+16)
					# tested in game, you can build up to 256 exactly... 0-256...
					# however, "Y (256) must be in range of 0 to 255" as required by anvil-parser
					if include_bedrock:
						chunk_range_y = range(256)
					else:
						# excluding y=0 as it is always bedrock... way more efficient for almost all worlds
						chunk_range_y = range(1,256)
					printv("chunk bounds y:",chunk_range_y[0],chunk_range_y[len(chunk_range_y)-1],"including bedrock?:",include_bedrock)
					printv("chunk bounds x:",global_chunk_range_x[0],global_chunk_range_x[len(global_chunk_range_x)-1])
					printv("chunk bounds z:",global_chunk_range_z[0],global_chunk_range_z[len(global_chunk_range_z)-1])

					try:
						pre_chunk = anvil.Chunk.from_region(pre_region,local_chunk_x,local_chunk_z)
						post_chunk = anvil.Chunk.from_region(post_region,local_chunk_x,local_chunk_z)
						new_chunk = anvil.Chunk.from_region(new_region,local_chunk_x,local_chunk_z)

					except anvil.ChunkNotFound:
						printv(file,"chunk failed lol", local_chunk_x,local_chunk_z, "..", sys.exc_info()[0])
						#print("chunk failed bc it gone")
						#print(sys.exc_info()[0])
						#print(traceback.print_exc())
					except:
						print("chunk fail")
						print(sys.exc_info()[0])
						print(traceback.print_exc())
					else:
						# every block in the current chunk
						for block_y in chunk_range_y:
							for local_block_x in range(16):
								for local_block_z in range(16):
									block_count += 1
									printv("current block:",local_block_x,block_y,local_block_z)

									# global block coords
									# verified as accurate twice. once by coordinate tools and second by "in world at"
									global_block_x = glob_chunk_x*16+local_block_x
									global_block_z = glob_chunk_z*16+local_block_z

									printv("global coords:",global_block_x,block_y,global_block_z)

									# takes local chunk coords
									pre_block = pre_chunk.get_block(local_block_x,block_y,local_block_z)
									post_block = post_chunk.get_block(local_block_x,block_y,local_block_z)
									new_block = post_chunk.get_block(local_block_x,block_y,local_block_z)

									printv(pre_block)
									printv(post_block)

									#print("--")
									#print("1:", global_block_x, global_block_z) # global block coords
									#print("2:", local_chunk_x, local_chunk_z) # chunk id
									#print("3:", global_block_x // 16, global_block_z // 16) # "in world at"
									#print("4:", local_chunk_x % 32, local_chunk_z % 32 ) # chunk id
									#print("--")

									if not (pre_block.id == post_block.id):
										#printp(file,"DIFFERENT BLOCK FOUND",pre_block.id,post_block.id)
										chunk_diff = True
										# if post world contains different block vs pre world, set output world block as post block
										# uses global block coordinates for some ungodly reason
										output_region.set_block(post_block, global_block_x, block_y, global_block_z)
									else:
										# if post and pre world blocks are same, set output world block as new world block
										output_region.set_block(new_block, global_block_x, block_y, global_block_z)

									if (not entitydataset) and chunk_diff and handle_entities:
										printv("saving entity data to chunk")
										entitydataset = True
										output_region.setEntities(post_chunk.getEntities(),global_block_x,global_block_z)
										output_region.setTileEntities(post_chunk.getTileEntities(), global_block_x, global_block_z)

					if chunk_diff:
						printv(file,"CHUNK DIFF", local_chunk_x,local_chunk_z)
						#print("CHUNK DIFF")
						#print(post_chunk.getEntities())
						#print(post_chunk.getTileEntities())
						#output_region.setEntities(post_chunk.getEntities(),)
						#output_region.setTileEntities(post_chunk.getTileEntities(),)
						#print(output_region.getEntities())
						#print(output_region.getTileEntities())

			#  [1]
			#print("POST:",check_x,check_y,check_z)

			# save output world region file
			file_to_save = str(wd_output_region) + 'r.' + str(region_x) + '.' + str(region_z) + '.mca'
			output_region.save(file_to_save)

			printp(file,"THREAD COMPLETED.... REGION PROCESSED.")
			return block_count



		else:
			# doesnt exist in pre-world, so all data within post-world is new....
			# for our case, ignore...
			# allow the output world to generate entirely new terrain. our world dimensions are set
			printp(file,"THREAD COMPLETED.... region file does not exist in all worlds, skipping")

			#printp(file,"------------------THREAD COMPLETED.... TERMINATING")
			return 0

# ::pre-threading code::
# for file in glob.glob("*.mca"):

# Make the Pool of workers
if len(filelist) < threads:
	print("using",len(filelist),"threads")
	pool = ThreadPool(len(filelist))
else:
	print("using",threads,"threads")
	pool = ThreadPool(threads)

# Open the files in their own threads
# and return the results
# for constants, use itertools.repeat(constant)
# file, wd_pre_region, wd_post_region, wd_new_region, wd_output_region, include_bedrock
threading_results = pool.starmap(process_region, zip(filelist, itertools.repeat(wd_pre_region), itertools.repeat(wd_post_region), itertools.repeat(wd_new_region), itertools.repeat(wd_output_region), itertools.repeat(include_bedrock)))


# Close the pool and wait for the work to finish
pool.close()
pool.join()

glob_blockcount = 0
for x in threading_results:
	glob_blockcount += x

print("THREADING RESULTS:",threading_results)



print("end region count:",file_count)
print(glob_blockcount, "blocks processed in total")
print("end chunk count:",chunks_processed)

print("--- %s seconds ---" % (time.time() - start_time))
