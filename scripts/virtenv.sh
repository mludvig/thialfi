#!/bin/sh

cd $(dirname $0)
source ../../bin/activate
exec python $*
