#!/usr/bin/python3
"""
This script will generate a list of all container images and all Tapis container images referenced by a tapis Kubernetes deployment folder.
To run this script you must first:
    * run the following at the root of the tapis-kube directory
      $ grep -r "image: " tapis-kube > images.txt  
      (NOTE: replace "tapis-kube" with the name of the actual directory)
    * place the images.txt file produced next to this script. 

"""
import argparse
import sys
import requests
import os
import subprocess


def get_all_images():
    """
    Reads a file, images.txt, in the cwd, and generates a list of docker images, one for each
    line in the file. This function can handle the output generated by
       grep -r "image: " tapis-kube > images.txt 

    """
    images = []
    if not os.path.exists('images.txt'):
        print("No images.txt file found, attempting to generate one...")
        # if no images.txt file in the pwd, try to generate one:
        proc = subprocess.run(["grep", "-r", '"image: "', "tapis-kube", ">", "images.txt"])
        print(f"Got return code: {proc.returncode}")

    with open('images.txt', 'r') as f:
        for line in f:
            # need to ignore this script which contains a code line with the text 'image:' in it:
            if 'admin/versionquery' in line:
                continue
            parts = line.split('image: ')
            if len(parts) > 1:
                i = parts[1].strip('\n')
                images.append(i)
    return images


def print_all_images(image_set):
    print("\n\nALL images:")
    print("***********")
    for i in image_set:
        print(i)

def get_tapis_images(image_set):
    tapis_image_prefixes = ['tapis', 'abaco', 'scleveland', ]
    tapis_images = []
    for i in image_set:
        for j in tapis_image_prefixes:
            if i.startswith(j):
                tapis_images.append(i)
                break
    return tapis_images



def get_image_data_from_docker_registry(image: str, tag: str):
    """
    Look up image metadata from Docker Hub for a specific image.
    Pass `image` as a fully qualified string without the tag, e.g., image="tapis/tenants-api"
    Pass `tag` as a string containing just the tag, no colon character, eg., tag="1.2.3"
    """
    base_url = "https://hub.docker.com"
    # The Docker Hub API required pagination, so we set a high number for page_size
    url = f"{base_url}/v2/repositories/{image}/tags?page_size=1000"
    try:
        rsp = requests.get(url)
        rsp.raise_for_status()
        data = rsp.json()
    except Exception as e:
        print(f"Error: unable to pull image data from Docker Hub API; details: {e}")
        return None
    # we expect a `results` item within the response that is a python list of dictionaries where
    # each dictionary container metadata about a specific tag. The fields include:
    #  * name -- the actual tag, e.g., "1.2.3" or "latest"
    #  * last_updated -- time stamp when the tag was last pushed to hub

    for item in data['results']:
        if item['name'] == tag:
            d = {
                "last_updated": item.get('last_updated'),
                "tag_last_pulled": item.get('tag_last_pulled'),
                "digest": item.get('digest')
            }
            # sometimes the digest only appears in the images key:
            if not d['digest']:
                try:
                    d['digest'] = item['images'][0]['digest']
                except:
                    print("Couldn't find digest in item or images. Giving up...")
            # print(f"found image: {image}:{tag}")
            if not d['last_updated']:
                print(f"Did not find last_updated for image: {image}:{tag}; data from docker: {item.get('last_updated')}")
            # NOTE: note warning on this one because we don't report it.
            # if not d['tag_last_pulled']:
            #     print(f"Did not find tag_last_pulled for image: {image}:{tag}; data from docker: {item.get('tag_last_pulled')}")
            if not d['digest']:
                print(f"Did not find digest for image: {image}:{tag}; data from docker: {item}")
            return d
    print(f"did not find image: {image}:{tag}")
    return None


def print_tapis_images(tapis_images):
    print("Extracted These Tapis Images From images.txt (Tag Removed):")
    print("***********************************************************")
    for i in tapis_images:
        print(i)


def print_tapis_images_with_data(tapis_images_with_data):
    print("\n\n")
    sp1 = " "*32
    sp2 = " "*20
    print(f"Image {sp1} Last Update Time {sp2} SHA-256:")
    print("***************************************************************************************")
    for i in tapis_images_with_data:
        image = i.get('image')
        last_updated = ""
        digest = ""
        if i.get('data'):
            last_updated = i.get('data').get('last_updated')
            digest = i.get('data').get('digest')
            if digest:
                digest = digest[:25]
            sp = " "*(37-len(image))
            print(f"{image}{sp}{last_updated} {digest}")
        else:
            sp = " "*(37-len(image))
            print(f"{image}{sp}***** NOT FOUND !!! *****")


def main():
    parser = argparse.ArgumentParser(description='Check Tapis image versions.')
    parser.add_argument("-d", "--diff", action="store_true", help="Diff images across environments; requires an images.txt file.")
    parser.add_argument("-t", "--tag", help="Image tag to use in the diff comparison; required if passing the --diff flag.")
    parser.add_argument("-f", "--fulldiff", action="store_true", help="Print the full image diff; Optional when passing the --diff flag. (Default is to only print differences)")
    args = parser.parse_args()
    diff_tapis_images = False
    print_full_diff = False
    if args.diff:
        diff_tapis_images = True
        print_full_diff = args.fulldiff 
        if not args.tag:
            print("Error: tag is required when passing the --diff command")
            sys.exit(1)
        print(f"Will perform image diff using tag: {args.tag}")

    images = get_all_images()
    image_set = set(images)
    tapis_images = get_tapis_images(image_set)
    tapis_images_without_tag = []
    tapis_images_with_data = []
    for full_image in tapis_images:
        # this `full_image` includes the tag, so we need to split it out:
        parts = full_image.split(":")
        image = parts[0]
        tapis_images_without_tag.append(image)
        # the full image should include the tag -- if it does not, we print an error and 
        # move on:
        if not len(parts) > 1:
            print(f"Error: could not get tag from image: {full_image}... skipping.")
            continue
        tag = parts[1]
        # strip extra characters from the tag:
        tag = tag.strip()
        if not diff_tapis_images:
            image_data = get_image_data_from_docker_registry(image, tag)
            tapis_images_with_data.append({"image": full_image, "data": image_data})
    print_tapis_images(tapis_images_without_tag)
    if diff_tapis_images:
        print("\nDiffing Tapis images...\n")
        tags = ["dev", "staging", args.tag]
        for image in tapis_images_without_tag:
            # the list of data for this image, one for each tag
            image_data = []    
            for tag in tags:
                data = get_image_data_from_docker_registry(image, tag)
                if not data or not hasattr(data, "get"):
                    data = {
                            "last_updated": "does not exist",
                            "tag_last_pulled": "does not exist",
                            "digest": "does not exist",
                            }
                image_data.append(data)
            # decide whether to print the image and all of its tags
            # first, we always print if there is any difference
            image_digests = set([d.get('digest') for d in image_data])
            if len(image_data) < 3 or len(image_digests) > 1:
                print(f"Found Difference for image: {image}")
                for idx, d in enumerate(image_data):
                    print(f"  {tags[idx]}: {d['digest']}")

            # otherwise, we print if doing a full diff
            elif print_full_diff:
                print(f"image: {image}")
                for idx, tag in enumerate(tags):
                    print(f"  {tag}: {image_data[idx]['digest']}")

    if not diff_tapis_images:
        print_tapis_images_with_data(tapis_images_with_data)


if __name__ == "__main__":
    main()
