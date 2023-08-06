#!/bin/bash

# parse args
while getopts b:d:f:o:t option
do
  case "${option}"
    in
    b) BUCKET=${OPTARG};;
    d) DATE=${OPTARG};;
    f) FILE=${OPTARG};;
    o) OUTPUT=${OPTARG};;
    t) TEST="--test"
  esac
done

if [ $TEST ] ; then
  export ELEX_RECORDING="flat"
  export ELEX_RECORDING_DIR="${OUTPUT}/recordings/${DATE}"
fi

# grab elex results for everything
if [ $FILE ]
  then
    elex results ${DATE} ${TEST} --national-only -o json -d ${FILE} > master.json
  else
    elex results ${DATE} ${TEST} --national-only -o json > master.json
fi

cp master.json reup.json

for file in "$OUTPUT"/election-config/* ; do
  if [ -e "$file" ] ; then
    elections=`cat $file | jq '.elections'`
    levels=`cat $file | jq '.levels'`
    path=`cat $file | jq -r '.output_path'`
    mkdir -p "$(dirname "$path/p")"

    # filter results
    if [ -s master.json ] ; then
      cat master.json \
      | jq -c --argjson elections "$elections" --argjson levels "$levels" '[
        .[] |
        if (.officeid == "H" and .level != "state") then empty else (
          select(.raceid as $id | $elections|index($id)) |
          select(.level as $level | $levels|index($level)) |
          {
            fipscode: .fipscode,
            level: .level,
            polid: .polid,
            polnum: .polnum,
            precinctsreporting: .precinctsreporting,
            precinctsreportingpct: .precinctsreportingpct,
            precinctstotal: .precinctstotal,
            raceid: .raceid,
            runoff: .runoff,
            statepostal: .statepostal,
            votecount: .votecount,
            votepct: .votepct,
            winner: .winner
          }
        ) end
      ]' > "$path/results.json"
    fi
  fi
done

# deploy to s3
if [ $BUCKET ] ; then
  aws s3 cp ${OUTPUT}/election-results/ s3://${BUCKET}/election-results/ --recursive --acl "public-read" --cache-control "max-age=5"
fi