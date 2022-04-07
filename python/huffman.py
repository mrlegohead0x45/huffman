#!/usr/bin/env python3

import sys
from argparse import ArgumentParser
from collections import Counter, namedtuple
from io import BytesIO
from json import dumps, loads
from struct import pack, unpack

parser = ArgumentParser(
    description="Huffman compression, decompression and visualisation. "
    "Compression by default, decompression with -d and visualisation with -v. "
    "Visualisation requires pydot and graphviz to be installed."
)
parser.add_argument(
    "infile", nargs="?", help="file to read input from, by default stdin"
)
parser.add_argument(
    "outfile", nargs="?", help="file to write output to, by default stdout"
)
parser.add_argument(
    "-d",
    "--decompress",
    action="store_true",
    help="decompress instead of compress (other options work the same)",
)
parser.add_argument(
    "-v",
    "--visualise",
    action="store_true",
    help="visualise the tree. (requires pydot and graphviz). "
    "the tree is written to huffman_tree.png",
)

# container for letter and frequency
Letter = namedtuple("Letter", ["char", "freq"])


class HuffmanException(Exception):
    pass


class Node:
    def __init__(self, letter: Letter) -> None:
        self.letter = letter
        self.leftNode = None
        self.rightNode = None
        self.hasChildNodes = False

    def asDict(self) -> dict | str:
        if self.hasChildNodes:
            return {"0": self.leftNode.asDict(), "1": self.rightNode.asDict()}
        else:
            return self.letter.char


def getName(node: Node) -> str:
    return escape(node.letter.char) + "\n(" + str(node.letter.freq) + ")"


def escape(s: str) -> str:
    # escape the names so they can be used in graphviz
    s = s.replace("\n", "\\\\n").replace("\t", "\\\\t").replace("\r", "\\\\r")
    return s


def makeTree(text: str, visualise: bool = False) -> Node:
    # make a list of Letter objects from the list of input characters
    letters = list(map(Letter._make, Counter(text).most_common()))

    # turn them all into singular nodes
    nodes = list(map(Node, letters))

    if visualise:
        import pydot

        # make a top down graph with pydot
        graph = pydot.Dot(graph_type="digraph")
        graph.set_rankdir("BT")

    # if there is only one letter
    # handle it separately
    if len(nodes) == 1:
        # make a root node that has the one letter
        root = Node(nodes[0].letter)
        root.hasChildNodes = True
        # make the left node the one letter
        root.leftNode = nodes[0]
        # make the right node empty
        root.rightNode = Node(Letter("", 0))
        # now root looks like this (if a is the only letter):
        #   root
        #   /  \
        #  a    empty
        nodes = [root]

        # add it to the graph
        if visualise:
            # here we have to add spaces to distinguish the root node and the one letter node
            name = escape(root.letter.char) + "\n (" + str(root.letter.freq) + ") "
            leftName = getName(root.leftNode)
            rightName = getName(root.rightNode)
            graph.add_node(pydot.Node(name))
            graph.add_node(pydot.Node(leftName))
            graph.add_node(pydot.Node(rightName))
            graph.add_edge(pydot.Edge(leftName, name))
            graph.add_edge(pydot.Edge(rightName, name))

    else:
        while len(nodes) > 1:
            # get last 2 letters
            leastCommon = nodes.pop()
            secondLeastCommon = nodes.pop()

            nodeLetter = Letter(
                leastCommon.letter.char + secondLeastCommon.letter.char,
                leastCommon.letter.freq + secondLeastCommon.letter.freq,
            )

            # make a new node with the two letters
            node = Node(nodeLetter)
            node.hasChildNodes = True
            node.leftNode = leastCommon
            node.rightNode = secondLeastCommon

            if visualise:
                name = getName(node)
                leftName = getName(node.leftNode)
                rightName = getName(node.rightNode)

                # add the new node to the graph
                graph.add_node(pydot.Node(name))

                # add it's children to the graph
                graph.add_edge(pydot.Edge(leftName, name))
                graph.add_edge(pydot.Edge(rightName, name))

            # add it back in
            nodes.append(node)

            # sort
            nodes.sort(reverse=True, key=lambda node: node.letter.freq)

    # get first (hopefully only) element in nodes
    (tree,) = nodes
    if visualise:
        graph.write_png("huffman_tree.png")

    return tree


def compress(text: str, tree: Node) -> str:
    allBits = ""

    for char in text:
        node = tree
        bits = ""

        if char not in tree.letter.char:
            raise HuffmanException(
                "Cannot compress character that is not in tree, "
                f"got {char!r}, chars in tree {tree.letter.char!r}"
            )

        while node.hasChildNodes:
            if char in node.leftNode.letter.char:
                node = node.leftNode
                bits += "0"

            elif char in node.rightNode.letter.char:
                node = node.rightNode
                bits += "1"

        allBits += bits

    return allBits


def encode(bits: str, tree: Node) -> bytes:
    output = b""

    treeAsJson = dumps(tree.asDict(), separators=(",", ":")).encode()
    output += pack(">i", len(treeAsJson))
    output += treeAsJson

    # encode the bits as chunks of 64 bits

    chunks = [bits[i : i + 64] for i in range(0, len(bits), 64)]
    output += pack(">Q", len(chunks))

    # loop through the chunks
    for chunk in chunks:
        # calculate the number of leading zeroes as this is lost when we convert to int
        leadingZeroes = len(chunk) - len(chunk.lstrip("0"))
        output += bytes([leadingZeroes])
        output += pack(">Q", int(chunk, 2))

    return output


def decode(b: bytes) -> tuple[str, dict]:
    fileobj = BytesIO(b)

    (treeLen,) = unpack(">i", fileobj.read(4))
    tree = loads(fileobj.read(treeLen))

    (noOfChunks,) = unpack(">Q", fileobj.read(8))

    bits = ""
    for _ in range(noOfChunks):
        (leadingZeroes,) = fileobj.read(1)

        # raise an exception if we have more than 64 leading zeroes in this chunk
        # (max 64 because that's how long the chunks are)
        if leadingZeroes not in range(0, 65):
            raise HuffmanException(
                f"Cannot have more that 64 leading zeroes in a chunk, got {leadingZeroes!r}"
            )

        (chunk,) = unpack(">Q", fileobj.read(8))
        bits += ("0" * leadingZeroes) + bin(chunk)[2:]  # remove "0b" at start

    return bits, tree


def decompress(bits: str, tree: dict) -> str:
    output = ""
    curr = tree

    for bit in bits:
        # if a key is not 0 or 1, raise an exception
        if (keys := list(curr.keys())) not in [["0", "1"], ["1", "0"]]:
            raise HuffmanException(f"Malformed tree, keys should be 0 or 1, got {keys}")

        curr = curr.get(bit)

        # if we reached a character
        if isinstance(curr, str):
            output += curr

            # go back to the top
            curr = tree
            continue

    return output


def main(args_list: list[str]) -> None:
    args = parser.parse_args(args_list)

    # set up the files to read from and write to
    # if we are decompressing, we need to read in binary mode
    stdin = sys.stdin.buffer if args.decompress else sys.stdin
    inMode = "rb" if args.decompress else "r"
    infile = open(args.infile, inMode) if args.infile else stdin

    # if we are compressing, we need to write in binary mode
    compressing = not args.decompress
    stdout = sys.stdout.buffer if compressing else sys.stdout
    outMode = "wb" if compressing else "w"
    outfile = open(args.outfile, outMode) if args.outfile else stdout

    with infile as file:
        inText = file.read()

    if args.decompress:
        bits, tree = decode(inText)
        out = decompress(bits, tree)

    else:
        tree = makeTree(inText, args.visualise)
        bits = compress(inText, tree)
        out = encode(bits, tree)

    with outfile as file:
        file.write(out)


if __name__ == "__main__":
    main(sys.argv[1:])
