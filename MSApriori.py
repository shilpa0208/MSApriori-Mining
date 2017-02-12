import re
import operator as o 
import itertools


def main():
	F = []
	formDataSet = []

	dataSet = readDataFromFile('input-data.txt')
	#dataSet = readDataFromFile('data-2.txt')
	#dataSet = readDataFromFile('tr1.txt')

	n= len(dataSet)

	for line in dataSet:
		line = getProcessedDataSet(line)
		formDataSet.append(line)

	paraSet = readDataFromFile('parameter-file.txt')
	#paraSet = readDataFromFile('para2-1.txt')
	#paraSet = readDataFromFile('pr1.txt')

	items, MISdict, SDC, mustHave, cannotBeTogetr, flag = getItems(paraSet)

	M = sorted(MISdict.items(),key=o.itemgetter(1))
	L, SCdict = initPass(M,formDataSet, MISdict, n)
	F1 = getF1values(L, MISdict, n, SCdict)
	F.append(F1)
	
	k=2
	while (len(F[k-2]))>0:
		if k==2:
			Ck = level2CandGen(L, SDC, MISdict, SCdict, n)

		else:
			Ck = MSCandGen(F[k-2],SDC, MISdict, SCdict, n)
		
		Fk = []
		for c in Ck:
			count = getSupportCount(c, formDataSet)
			if (count/n)>=float(MISdict[c[0]]) and (canBeTogetr(c, cannotBeTogetr, flag)):
				Fk.append(c)
			
		F.append(Fk)
		k+=1
		if len(F[k-2-1])==0:
			break
	printOutput(F, SCdict, mustHave, cannotBeTogetr, formDataSet, Ck)


def getItems(paraSet):
	items = []
	dic = {}
	for param in paraSet:
		param = param.rstrip('\n')
		if '=' in param:
			param = param.split('=')
			param = [par.strip(' ') for par in param]
			res = re.search(r"^MIS\(([a-zA-Z0-9]+)\)",param[0],re.M|re.I)
			if res:
				item = res.group(1)
				items.append(item)
				dic[item]=param[1]
			else:
				if param[0]=='SDC':
					SDC = param[1]
		else:
			param = param.split(':')
			param = [par.strip(' ') for par in param]
			if param[0]=='must-have':
				mustHave = param[1].split('or')
				mustHave = [val.strip(' ') for val in mustHave]
			else:
				count = 0
				for ch in param[1]:
					if ch == '{':
						count+=1
				if count==1:
					cannotBeTogetr = param[1]
					cannotBeTogetr = param[1].strip('{').strip('}')
					cannotBeTogetr = cannotBeTogetr.split(',')
					cannotBeTogetr = [val.strip(' ') for val in cannotBeTogetr]
				else:
					CBT = param[1]
					CBT = CBT.split('}, {')
					cannotBeTogetr = []
					for i in range(0,len(CBT)):
						temp_list = []
						temp = list(map(int, re.findall(r'\d+',CBT[i])))
						for j in range(0, len(temp)):
							temp_list.append(str(temp[j]))
						cannotBeTogetr.append(temp_list)
			flag = count
	return items, dic, SDC, mustHave, cannotBeTogetr,flag  
		
			
def readDataFromFile(file):
	with open(file) as f:
		inpData = f.readlines()
	return inpData

	
def getProcessedDataSet(line):
	line = line.rstrip('\n')
	line = line.strip('{')
	line = line.strip('}')
	line = line.split(',')
	line = [item.strip(' ') for item in line]
	return line	

def initPass(M, dataSet, MISdic, n):
	SCdict = {}
	items = []
	L = []
	items = [tup[0] for tup in M]
	
	for item in items:
		count = 0;
		for dset in dataSet:
			if item in dset:
				count+=1;
		SCdict[item] = count

	for item in items:	
		if (SCdict[item]/n)>=float(MISdic[item]):
			minMIS = MISdic[item]
			index = items.index(item)
			L.append(item)
			break
	i=0
	for i in range(index+1,len(items)):
		currItem = items[i]
		if (SCdict[currItem]/n) >= float(minMIS):
			L.append(currItem)
		i+=1
	return L, SCdict


def getF1values(L, MISdict, n, SCdict):
	F1 = []
	for item in L:
		if(SCdict[item]/n)>=float(MISdict[item]):
			F1.append(item)
	return F1


def getTailCount(c, dataSet):
	tailCount = 0
	for t in dataSet:
		if set(c[1:])<=set(t):
			tailCount+=1
	return tailCount


def level2CandGen(L, SDC, MISdict, SCdict, n):
	C2 = []
	for l in range(0,len(L)):
		if float(SCdict[L[l]]/n)>=float(MISdict[L[l]]):
			for h in range(l+1,len(L)):
				if ((SCdict[L[h]]/n) >= float(MISdict[L[l]]) and abs((SCdict[L[h]]/n) - (SCdict[L[l]]/n)) <= float(SDC)):
					C2.append([L[l],L[h]])
	return C2


def MSCandGen(F, SDC, MISdict, SCdict, n):
	Ck = []
	fjoinSet = []
	subsets = []
	
	for i in range(0,len(F)):
		for j in range(i+1,len(F)):
				item1 = F[i]
				item2 = F[j]
				joinSet = getJoinSet(item1, item2, SDC, MISdict, SCdict, n)
				if joinSet!= None:
					fjoinSet.append(joinSet)
	
	Ck = fjoinSet
	found = False
	for val in fjoinSet:
		subsets = getSubsets(val)
		for asubset in subsets:
			if set(val[0])<=set(asubset) or (MISdict[val[1]]==MISdict[val[0]]):
				for item in F:
					if set(asubset) in set(item):
						found = True
						break
				if found==False:
						Ck.remove(val)
						break	
	return Ck


def getSubsets(val):
    res = []
    for combo in itertools.combinations(val, len(val)-1):
        res.append(list(combo))
    return res


def getJoinSet(item1, item2, SDC, MISdict, SCdict, n):
	joinSet = []

	if(len(item1)!=len(item2)):
		return None
		
	for i in range(0,len(item1)-1):
		if item1[i]!=item2[i]:
			return None
	
	if (item1[len(item1)-1])==(item2[len(item2)-1]):
		return None
	
	if abs((SCdict[item1[len(item1)-1]]/n)-(SCdict[item2[len(item2)-1]]/n))>float(SDC):
		return None
		
	for i in range(0,len(item1)-1):
		joinSet.append(item1[i])
	
	if(MISdict[item1[len(item1)-1]]<MISdict[item2[len(item2)-1]]):
		joinSet.append(item1[len(item1)-1])
		joinSet.append(item2[len(item2)-1])
	else:
		joinSet.append(item2[len(item2)-1])
		joinSet.append(item1[len(item1)-1])

	return joinSet


def printOutput(F, SCdict, mustHave, cannotBeTogetr, dataSet, Ck):
	opfile = open('MSAprioriOpt.txt','w')
	for i in range(0,len(F)):
		count = 0
		
		if i==0:
			for item in F[i]:
				if item in mustHave:
					count+=1

					if count == 1:
						print('Frequent '+str(i+1)+'-itemsets\n')
						opfile.write('Frequent '+str(i+1)+'-itemsets\n')

					print('\t'+str(SCdict[item])+' : {'+str(item)+'}\n')
					opfile.write('\t'+str(SCdict[item])+' : {'+str(item)+'}\n')
			
			if count > 0:
				print('Total number of frequent 1-itemsets = '+str(count)+'\n')
				opfile.write('Total number of frequent 1-itemsets = '+str(count)+'\n')
		else:
			for item in F[i]:
				for val in mustHave:
					if val in item:
						count+=1

						if count == 1:
							print('Frequent '+str(i+1)+'-itemsets\n')
							opfile.write('Frequent '+str(i+1)+'-itemsets\n')

						print('\t'+str(getSupportCount(item, dataSet))+' : {'+str(",".join(item)[0:])+'}')
						opfile.write('\t'+str(getSupportCount(item, dataSet))+' : {'+str(",".join(item)[0:])+'}\n')
						print('Tailcount = '+str(getTailCount(item, dataSet))+'\n')
						opfile.write('Tailcount = '+str(getTailCount(item, dataSet))+'\n')
						break
		
			if count > 0:
				print('Total number of frequent '+str(i+1)+'-itemsets = '+str(count)+'\n')
				opfile.write('Total number of frequent '+str(i+1)+'-itemsets = '+str(count)+'\n')
	opfile.close()
		

def getSupportCount(item, dataSet):
	count = 0
	for t in dataSet:
		if set(item)<=set(t):
			count+=1
	return count


def canBeTogetr(c, cannotBeTogetr, flag):
	if flag == 1:
		if set(cannotBeTogetr)<=set(c):
			return False
	else:
		for val in cannotBeTogetr:
			if set(val)<=set(c):
				return False
	return True


if __name__ == '__main__':
	main()