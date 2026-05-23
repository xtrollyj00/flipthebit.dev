---
title: "Cache me if you can #1: An intro to what caches are and why you need one"
date: "2024-11-26"
tags:
  - "Cache me if you can"
  - "data locality"
  - "cache"
---

My theoretical computer science professor once remarked, “What do IT professionals say when
there's a performance issue? Let’s add another cache! :smile:” When dealing with memory systems,
it’s common to encounter saturation of throughput or pipeline stalls caused by unpredictable
and high read/write latency. Implementing caches can effectively eliminate this bottleneck in most cases.

Unfortunately, the performance of a system is limited by its weakest component. In modern computing,
processors have scaled remarkably well, with their performance increasing by approximately 100 times
since 1999. However, this improvement does not extend to memory systems. Since 1999:
- DRAM capacity has increased by 128 times,
- DRAM bandwidth has increased by only 20 times,
- DRAM latency has been reduced by only 1.2 times.

This is precisely why 40-70% of the die area of modern CPU chips is dedicated to data interconnects,
caches, and memory controllers.

If the die-area of caches still does not make sense to you (to me, it is still a small mystery :smile:),
I will try to explain. Caches seem to be huge, but they still have a limited size. Compared to the
capacity of a DRAM chip (a few gigabytes), they're tiny (L3 cache, a few MB). Smaller size is key
to achieving higher throughput and lower latency, but it has its challenges.

## The challenge

It's not possible to fit an entire DRAM into a cache :smile:. A cache has to select a subset of memory
to store, and it has to be smart about choosing this subset. Caches exploit something called data
locality. In a nutshell, data that's been used is likely to be used again. However, there are different
types of data locality.

### Spatial locality

Imagine you are looping an array of integers and incrementing every element inside it.

```c
for (int i = 0; i < ARRAY_SIZE; i++) {
    array[i]++;
}
```
In this loop, a cache can take advantage of spatial locality because the next address the program
will access is nearby the address that was accessed before. When you first access an array, several
elements are loaded into one cache line, which means you don't have to make as many read/write
requests to DRAM. This is called a *sequential access pattern*. Data structures that don't use
sequential access are usually hash tables. These use a *random access pattern*. While you're
exploiting spatial locality, the bottleneck is cache line size.

### Temporal locality

Temporal locality is the tendency of programs to use data items over and over again during their
execution. In our loop example, we could say that variable `i` exhibits temporal locality because
it is incremented at the end of each loop (ignoring the fact that it is stored in a CPU register).
The only limiting factor here is the size of the cache.

There are other types of locality that are derivatives of these two. Caches determine the working
subset of memory based on data locality using cache replacement policies. These will be discussed
in my next post.

## What is a cache?

In my opinion, cache can be called anything, which is able to:
- Reduce the number of read/write requests, thus reducing required throughput of a memory system.
- Reduce the latency of read/write requests.

As this is an FPGA blog, I will refer to caches as components of a memory system implemented in
FPGA logic that do the things mentioned above.

### Fully associative cache

{{<
    dynamic-image
    light="img/fully-assoc-light.svg"
    dark="img/fully-assoc-dark.svg"
    alt="Fully Associative Cache"
>}}

The figure above shows a fully associative cache with a capacity of 4 elements. This is the simplest
type of cache to design, but it consumes a huge amount of area on the chip, as there needs to be
exactly one address comparator for each element stored in the cache. When a core tries to read an
address, it is compared with the addresses of all the elements stored in the cache. If a match is
found, data is returned. This is called a **cache hit**, and the data is available almost immediately.
A fully associative cache has the best collision properties - a collision cannot happen, we can
simply run out of space. However, this solution does not scale very well:
- Address comparators cost lot of chip area.
- Huge combinatorial path - low operating frequency.

### Direct mapped cache

Here we go, another simple and obvious solution. Run the key (address) through a hash function,
use the hash as an address in the block RAM, read the data, compare the key - data is in the
cache or not. This variant is as scalable as block RAMs. There is a small caveat - the hash
function can introduce too much randomness:
1. A programmer cannot easily determine cache utilisation.
2. We need to store whole address for comparison.

Let us do an upgrade. We want to design a cache with a capacity of 512 elements - we need 9
bits to address inside the block RAM. The total address is 32 bits. We will divide
the address into two parts:
- **tag** (most significant 23 bits),
- **index** (least significant 9 bits).

Index is used to address data in the cache. Tag is used to validate that the data in
the cache is the data we are looking for - it is our key. Now a programmer can predict
what data will be cached, and we have saved 29% of block RAM area.

Remember spatial locality? We can't exploit it in this variant, we only store one byte of
data in a cache line. So we introduce it into our design with another trick. We want to store 64B
(corresponds to 16 integers) in a cache line, so we split the address into three parts:
- **tag** (most significant 17 bits),
- **index** (9 bits),
- **offset** (least signigicant 6 bits).

{{<
    dynamic-image
    light="img/direct-mapped-light.svg"
    dark="img/direct-mapped-dark.svg"
    alt="Directly mapped cache"
>}}

This way, when we iterate an array, data elements that we will access later are cached for
the program. Now we have a scalable cache, but collisions are very likely to happen. When
a collision or **cache miss occurs**, the cache needs to evict the current cache line and replace
it with a new one. Evicting a cache line introduces a latency penalty. Another problem is that
the cache cannot choose which data to store. This is why our smart colleagues developed
the **set associative cache**.

### Set associative cache

{{<
    dynamic-image
    light="img/set-assoc-light.svg"
    dark="img/set-assoc-dark.svg"
    alt="Set associative cache"
>}}

Set associative cache can be considered as a fully associative cache inside a direct mapped cache
:smile:. The principle of address division will be the same. On the other hand, there will not be
one cache line in each index, but several. This way the cache can choose which cache line to evict
in the case of cache miss. The best cache line to evict is determined by the **cache replacement policy**.
The number of cache lines in an address is called cache **associativity**.

This solution provides a way to scale your cache as you wish. If you need higher frequency, use can
reduce the associativity of your cache. If your timing is too good, you can squeeze the most out of
your cache by increasing the associativity. Don't be afraid to experiment, that's the beauty of FPGAs.

## Conclusion

At the end of the day, caches are a clever way to work around the limits of memory systems. They might
not fix every problem, but they sure do a great job of speeding things up most of the time. From simple
fully associative caches to more advanced set associative ones, they’ve come a long way in squeezing
the most out of available resources.

Still, they’re not magic. Collisions, limited size, and the occasional penalty for evicting data are
just part of the game. For FPGA-based designs, though, they’re a playground for crafting custom
solutions tailored to specific needs. As a natural follow-up, I’ll dive into one of the most
fascinating and well-researched topics in caching today: **cache replacement policies**.

Ultimately, while caches are not a universal solution to memory bottlenecks, they are an indispensable
tool in the quest for higher performance and efficiency in computing. Understanding and optimizing
their design is key to unlocking the full potential of modern systems—and perhaps, in the spirit of my
professor's quip, there’s always room to add one more cache :grin:.
