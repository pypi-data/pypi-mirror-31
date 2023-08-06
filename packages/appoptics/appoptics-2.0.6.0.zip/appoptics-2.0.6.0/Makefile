# ----The Makefile for automated building (and hopefully) deployment
SHELL=bash

.DEFAULT_GOAL := nothing

# All the variables
# # LIBOBOE is the name of the liboboe shared library
LIBOBOEORG := $(shell  if [ -f /etc/alpine-release ]; then  echo "liboboe-1.0-alpine-x86_64.so.0.0.0" ; else echo "liboboe-1.0-x86_64.so.0.0.0" ; fi)
LIBOBOE := "liboboe-1.0-x86_64.so.0.0.0"
OBOEVERSION = "2.0.10"

# # When you run 'make fetch-latest-code' it will use the current branch and reset it the the
# # latest commit, so make sure you have committed all of your local changes before you run
# # this target.
current_branch :=$(shell git symbolic-ref HEAD | sed 's!refs\/heads\/!!')
confirmed := "No"

# It does nothing with just a 'make', avoid mistakenly messing up your environment.
nothing:
	@echo -e "\nHow can I help you?"
	@echo -e "  - 'make local':"
	@echo -e "          Make an agent package from local code and upload it to packagecloud for tests."
	@echo -e "  - 'make dev':"
	@echo -e "          Make an agent package from HEAD of current branch and upload it to packagecloud for tests."
	@echo -e "  - 'make appoptics-package':"
	@echo -e "          Just build the package."
	@echo -e "  - 'make release':"
	@echo -e "          (WARNING: make sure you know what you are doing.)"
	@echo -e "          Build the agent package from master branch and release it to pypi."
	@echo -e "Check the Makefile for other targets/options.\n"
	
# TODO: Install SWIG if it is not there.
check-swig:
	@echo -e "Is SWIG installed?"; \
		command -v swig >/dev/null 2>&1 || \
		{ echo >&2 "Swig is required to build the distribution. Aborting."; exit 1;}
	@echo -e "Yes."

# Download the pre-compiled liboboe shared library from AWS.
# You'd better pay attention that this library might be out of date.
download-liboboe:
	@echo -e "Downloading liboboe:${LIBOBOE}  the shared library.\n"; \
		( cd appoptics/swig; \
		curl -o ${LIBOBOE}  "https://files.appoptics.com/c-lib/${OBOEVERSION}/${LIBOBOEORG}"; \
		ln -sf ${LIBOBOE} liboboe-1.0.so; \
		ln -sf ${LIBOBOE} liboboe-1.0.so.0 )

# Download liboboe header files to build the Python wrapper
# You'd better pay attention that these headers might be out of date.
download-headers:
	@echo -e "Downloading header files (.hpp, .h, .i)"; \
		( cd appoptics/swig; \
		echo "Downloading ${OBOEVERSION}" files:; \
		for i in VERSION oboe.h oboe.hpp oboe.i oboe_debug.h; do \
			echo "Downloading $$i"; \
			curl -O "https://files.appoptics.com/c-lib/${OBOEVERSION}/$$i"; \
		done )

download-all: download-headers download-liboboe

# Build the Python wrapper from liboboe headers
wrapper: check-swig download-headers download-liboboe
	@echo -e "Generating SWIG wrapper for C/C++ headers."; \
		( cd appoptics/swig; \
		./gen_bindings.sh )

# Fetch the latest commits of the current branch from github
fetch-latest-code-from-current-branch:
	@echo -e "Fetching latest code from orign/$(current_branch)."; \
		git stash; \
		git fetch origin; \
		git reset --hard origin/$(current_branch)

# Fetch the latest commits of master from github
fetch-latest-code-from-master:
	@echo -e "Fetching latest code from orign/master."; \
		git stash; \
		git checkout master; \
		git fetch origin; \
		git reset --hard origin/master

# Build the Python agent package.
appoptics-package: wrapper
	@echo -e "Generating python agent package"; \
		python setup.py sdist
	@echo -e "\nDone."

# Resume your workspace
resume-workspace:
	-git stash pop

# Go through the build process but upload it to packagecloud for internal tests.
local: appoptics-package upload-to-packagecloud clean
	@echo -e "Built the agent package from local code and uploaded to packagecloud.io"

# Go through the build process but upload it to packagecloud for internal tests.
dev: fetch-latest-code-from-current-branch appoptics-package upload-to-packagecloud clean resume-workspace
	@echo -e "Built the agent package on current branch and uploaded to packagecloud.io"

# Go through the build process and release the package to pypi
release: are-you-sure fetch-latest-code-from-master appoptics-package upload-to-real-pypi clean resume-workspace
	@echo -e "Done: Built the agent package on master and uploaded it to pypi"

# Get confirmation
are-you-sure:
	@read -p "Are you sure? [Y/n]" -n 1 -r; \
	if [[ $$REPLY != "Y" ]]; then \
		echo -e -n "\nSee you. >> "; \
		exit 1; \
	fi
	@echo -e "\nGood, proceeding..."; \
		$(eval confirmed := "Yes")

# Upload the already built package to packagecloud, our fake pypi.
upload-to-packagecloud:
	@echo -e "Done: Uploaded the agent package to packagecloud."
	@echo -e "Not supported now, sorry."

# Upload the already built package to the real pypi
upload-to-real-pypi:
	@if [[ $(confirmed) != "Yes" ]]; then \
		echo -e "You cannot run this target directly, run 'make release' instead."; \
		exit 1; \
	fi
	@echo -e "------------------------The Last Step: Do It By Yourself-----------------------------"
	@echo -e "(Just for the first time you need: 'python setup.py sdist register')"
	@echo -e "---------Run: 'python setup.py sdist upload' to release it to pypi.python.org--------"
	@echo -e "(You might need to make sure your ~/.pypirc is in order)"

bumpversion:
	@echo -e " "; \
		command -v bumpversion >/dev/null 2>&1 || \
		{ echo >&2 "bumpversion is required to bump version. to install, run: pip install bumpversion. Aborting."; exit 1;}
	@read -p "Input m for major, r for minor, p for patch: " -n 1 -r; \
	if [[ $$REPLY == "m" || $REPLY == "M" ]]; then \
		echo -e -n "\nbump  major version..." ; \
		bumpversion major; \
		exit 0; \
	elif [[ $$REPLY == "r" || $REPLY == "R" ]]; then \
		echo -e -n "\nbump  minor version..." ; \
		bumpversion minor; \
		exit 0; \
	elif [[ $$REPLY == "p" || $REPLY == "P" ]]; then \
		echo -e -n "\nbump patch version..." ; \
		bumpversion patch ; \
	else \
		echo -e "invalid choice"; \
		exit 1; \
	fi

# clean up everything.
clean:
	@echo -e "Cleaning intermediate files."; \
		(cd appoptics/swig; rm -f VERSION oboe.py oboe_wrap.cxx _oboe.so liboboe-1.0*so*)
	@echo -e "Done."

.PHONY: nothing check-swig download-liboboe download-headers wrapper appoptics-package \
	fetch-latest-code-from-current-branch fetch-latest-code-from-master are-you-sure \
	local dev release upload-to-packagecloud upload-to-real-pypi clean resume-workspace
