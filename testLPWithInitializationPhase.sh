#bashrc

#for file in ../part3TestCases/unitTests/10/test*.dict
#do
#	output=$(echo $file | sed "s/.dict/.output/")
#    python testLPWithInitializationPhase.py < $file > "$output-2"
#    echo $output
#    diff $output "$output-2"
#done

for file in ../part3TestCases/unitTests/20/test*.dict
do
	output=$(echo $file | sed "s/.dict/.output/")
    python testLPWithInitializationPhase.py < $file > "$output-2"
    echo $output
    diff $output "$output-2"
done

#for file in ../part3TestCases/unitTests/50/test*.dict
#do
#    output=$(echo $file | sed "s/.dict/.output/")
#    python testLPWithInitializationPhase.py < $file > "$output-2"
#    echo $output
#    diff $output "$output-2"
#done
