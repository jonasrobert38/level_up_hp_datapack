from zipfile import ZipFile
import os
from os.path import basename

##     Datapack parameters    ##

start_with_hearts  = 5
end_with_hearts    = 20

#array should have (end_with_hearts - start_with_hearts) entries
hp_xp_per_level=[40,50,60,70,70,70,70,70,100,100,150,150,200,200,200]

## End of Datapack parameters ##

failed = True
print("You are running the Level Up HP! Datapack modifier!")
if start_with_hearts<1:
	print(f"PARAMETER ERROR: 'start_with_hearts' should be larger than 0. Parameter cannot be {start_with_hearts}.")
elif end_with_hearts<=start_with_hearts:
	print(f"PARAMETER ERROR: 'end_with_hearts' should be larger than 'start_with_hearts'.")
elif len(hp_xp_per_level)!=end_with_hearts-start_with_hearts:
	print(f"PARAMETER ERROR: hp_xp_per_level[] should have (end_with_hearts-start_with_hearts) entries ({end_with_hearts}-{start_with_hearts} -> {end_with_hearts-start_with_hearts} entries).")
else:
	failed = False
	hp_initialized_tag='hpinit'
	hp_xp='hpxp'
	hp_bossbar_cooldown='hpcd'
	hp_bossbar_cooldown_ticks=50
	total_kills='totk'
	hp_max_tag='hpmax'
	hp_level='hplvl'
	num_bossbars=50

	same=1
	sames=[]
	for idx in range(0,len(hp_xp_per_level)):
	    if idx+1 < len(hp_xp_per_level):
	        if hp_xp_per_level[idx]==hp_xp_per_level[idx+1]:
	            same+=1
	        else:
	            sames.append(same)
	            same=1
	    else:
	        sames.append(same)

	load_code='scoreboard objectives add '+hp_xp+' dummy\n'
	load_code+='scoreboard objectives add '+hp_level+' dummy\n'
	load_code+='scoreboard objectives add '+hp_bossbar_cooldown+' dummy\n'
	load_code+='scoreboard objectives add '+total_kills+' totalKillCount\n'

	for i in range(0,num_bossbars*len(sames)):
	    load_code+='bossbar add '+hp_xp+str(i)+' "HP EXP"\n'
	    load_code+='bossbar set '+hp_xp+str(i)+' max '+str(num_bossbars)+'\n'
	    load_code+='bossbar set '+hp_xp+str(i)+' style notched_10\n'
	    load_code+='bossbar set '+hp_xp+str(i)+' color red\n'
	    load_code+='bossbar set '+hp_xp+str(i)+' value '+str((i%num_bossbars)+1)+'\n'

	tick_code='scoreboard players set @a[tag=!'+hp_initialized_tag+'] '+hp_xp+' 0\n'
	tick_code+='scoreboard players set @a[tag=!'+hp_initialized_tag+'] '+hp_level+' 0\n'
	tick_code+='scoreboard players set @a[tag=!'+hp_initialized_tag+'] '+hp_bossbar_cooldown+' 0\n'
	tick_code+='tag @a[tag=!'+hp_initialized_tag+'] add '+hp_initialized_tag+'\n'
	tick_code+='scoreboard players add @a[scores={'+total_kills+'=1..},tag=!'+hp_max_tag+'] '+hp_xp+' 1\n'
	tick_code+='scoreboard players add @a[scores={'+hp_bossbar_cooldown+'=..'+str(hp_bossbar_cooldown_ticks)+'},tag=!'+hp_max_tag+'] '+hp_bossbar_cooldown+' 1\n'
	tick_code+='scoreboard players set @a[scores={'+total_kills+'=1..},tag=!'+hp_max_tag+'] '+hp_bossbar_cooldown+' 0\n'
	tick_code+='scoreboard players set @a[scores={'+total_kills+'=1..},tag=!'+hp_max_tag+'] '+total_kills+' 0\n'

	for i in range(0,len(hp_xp_per_level)):
		tick_code+='scoreboard players set @a[scores={'+hp_xp+'='+str(hp_xp_per_level[i])+'..,'+hp_level+'='+str(i)+'}] '+hp_level+' '+str(100*(i+1))+'\n'
		tick_code+='scoreboard players set @a[scores={'+hp_level+'='+str(100*(i+1))+'}] '+hp_xp+' 0\n'
		tick_code+='scoreboard players set @a[scores={'+hp_level+'='+str(100*(i+1))+'}] '+hp_level+' '+str(i+1)+'\n'
		tick_code+='execute as @a[scores={'+hp_level+'='+str(i)+'}] run attribute @s minecraft:generic.max_health base set '+str((start_with_hearts*2)+(2*i))+'\n'
	tick_code+='execute as @a[scores={'+hp_level+'='+str(len(hp_xp_per_level))+'}] run attribute @s minecraft:generic.max_health base set '+str(end_with_hearts*2)+'\n'

	minxp=0
	prev=0
	level_index=0
	iterations=0
	hadbossbars=-1
	for samecount in range(0,len(sames)):
		if sames[samecount]>1:
			for k in range(0,hp_xp_per_level[level_index]-1):
				cur=max(round(k*num_bossbars/(hp_xp_per_level[level_index]))+hadbossbars,0)
				if (cur>prev and ((cur+1)%50 != 0 or k==0) and (cur%50 != 0 or k==0)) or k==0:
					maxxp=k
					tick_code+='bossbar set minecraft:'+hp_xp+str(cur)+' players @a[scores={'+hp_xp+'='+str(minxp)+'..'+str(maxxp)+','+hp_level+'='+str(level_index)+'..'+str(level_index+sames[samecount]-1)+','+hp_bossbar_cooldown+'=..'+str(hp_bossbar_cooldown_ticks)+'}]\n'
					minxp=k+1
				prev=cur
			tick_code+='bossbar set minecraft:'+hp_xp+str(num_bossbars+hadbossbars-(samecount>0))+' players @a[scores={'+hp_xp+'='+str(maxxp+1)+'..,'+hp_level+'='+str(level_index)+'..'+str(level_index+sames[samecount]-1)+','+hp_bossbar_cooldown+'=..'+str(hp_bossbar_cooldown_ticks)+'}]\n'
		else:
			for k in range(0,hp_xp_per_level[level_index]-1):
				cur=max(round(k*num_bossbars/(hp_xp_per_level[level_index]))+hadbossbars,0)
				if (cur>prev and ((cur+1)%50 != 0 or k==0) and (cur%50 != 0 or k==0)) or k==0:
					maxxp=k
					tick_code+='bossbar set minecraft:'+hp_xp+str(cur)+' players @a[scores={'+hp_xp+'='+str(minxp)+'..'+str(maxxp)+','+hp_level+'='+str(level_index)+','+hp_bossbar_cooldown+'=..'+str(hp_bossbar_cooldown_ticks)+'}]\n'
					minxp=k+1
				prev=cur
			tick_code+='bossbar set minecraft:'+hp_xp+str(num_bossbars+hadbossbars-(samecount>0))+' players @a[scores={'+hp_xp+'='+str(maxxp+1)+'..,'+hp_level+'='+str(level_index)+','+hp_bossbar_cooldown+'=..'+str(hp_bossbar_cooldown_ticks)+'}]\n'
		minxp=0
		level_index+=sames[samecount]
		hadbossbars=50*(samecount+1)

	print("Writing load.mcfunction...")
	load_file = open("data/health/functions/load.mcfunction","w")
	load_file.write(load_code)
	load_file.close()
	print("Writing tick.mcfunction...")
	tick_file = open("data/health/functions/tick.mcfunction","w")
	tick_file.write(tick_code)
	tick_file.close()
	print("Updating datapack zipfile...")
	try:
		os.remove('Wofljes_Level_Up_HP.zip')
	except:
		print("Cannot remove datapack zipfile: Not found!")
	with ZipFile("Wofljes_Level_Up_HP.zip",'w') as zf:
		for folderName, subfolders, filenames in os.walk("data"):
			for filename in filenames:
				filePath = os.path.join(folderName,filename)
				zf.write(filePath, filePath)
	zf.close()
	print("Finished compiling datapack!")
if failed:
	print("Failed to modify Datapack, aborting...")