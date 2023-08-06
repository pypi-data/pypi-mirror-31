// **********************************************************************
//
// Copyright (c) 2003-2018 ZeroC, Inc. All rights reserved.
//
// This copy of Ice is licensed to you under the terms described in the
// ICE_LICENSE file included in this distribution.
//
// **********************************************************************

#ifndef ICE_INTERFACE_BY_VALUE_H
#define ICE_INTERFACE_BY_VALUE_H

#include <Ice/Value.h>
#include <Ice/OutputStream.h>
#include <Ice/InputStream.h>

#ifdef ICE_CPP11_MAPPING

namespace Ice
{

/**
 * Represents an instance of a Slice interface that was marshaled by value.
 * \headerfile Ice/Ice.h
 */
template<typename T>
class InterfaceByValue : public ValueHelper<InterfaceByValue<T>, Value>
{
public:
    /**
     * Obtains the Slice type ID of this exception.
     * @return The fully-scoped type ID.
     */
    virtual std::string ice_id() const
    {
        return T::ice_staticId();
    }

    /**
     * Obtains the Slice type ID of this exception.
     * @return The fully-scoped type ID.
     */
    static const std::string& ice_staticId()
    {
        return T::ice_staticId();
    }

    /**
     * Returns an empty tuple.
     * @return The empty tuple.
     */
    std::tuple<> ice_tuple() const
    {
        return std::tie();
    }
};

}

#endif

#endif
