#bashrc

#for file in $(find ../ilpTests/unitTests -iname 'ilpTest*[0-9]')
#do
#   echo $file
#   output="$file.output"
#   python testILP.py < $file > "$output-n"
#   echo $output
#   diff $output "$output-n"
#done

#for file in $(find ../ilpTests/unitTests -iname 'test*[0-9]')
#do
#   echo $file
#   output="$file.output"
#   python testILP.py < $file > "$output-n"
#   echo $output
#   diff $output "$output-n"
#done

#for file in ../ilpTests/assignmentTests/part*.dict
#do
#    echo $file
#    output=$(echo $file | sed "s/.dict/.output/")
#    python testILP.py < $file > "$output-n"
#    echo $output
#    diff $output "$output-n"
#done
