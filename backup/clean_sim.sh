#!/bin/bash
echo "cleaning kafka ..."
make reconft && make delr && make consumet
echo "done."


